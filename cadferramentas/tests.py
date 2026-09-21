from importlib import import_module
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, TestCase

from .models import FotoFerramenta, Ferramenta, LocalFerramenta
from principal.access import grupos_de_acesso
from principal.models import SolicitacaoAlteracao
from pontoele.models import Servidor


class ViewsImportTests(SimpleTestCase):
    def test_views_import_without_optional_export_dependencies(self):
        module = import_module("cadferramentas.views")
        self.assertTrue(hasattr(module, "cadferramentas"))


class HistoricoFerramentaTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="ferramenta_hist",
            email="ferramenta_hist@example.com",
            password="admin123",
        )
        self.user.groups.add(grupos_de_acesso()["Ferramentas"])

    def test_cadastrar_ferramenta_salva_possui_patrimonio(self):
        client = Client()
        client.force_login(self.user)

        response = client.post(
            "/ptmdsa/cadferramentas/cadastrar/",
            {
                "possui_patrimonio": "nao",
                "nome": "Alicate",
                "categoria": "MANUAL",
                "fabricante": "Bosch",
                "data_aquisicao": "2024-03-01",
                "valor_aquisicao": "1250.75",
                "estado": "NOVO",
                "local": "COFEN",
                "descricao": "Ferramenta de teste",
                "responsavel": "",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        ferramenta = Ferramenta.objects.latest("id")
        self.assertEqual(ferramenta.possui_patrimonio, "nao")
        self.assertEqual(ferramenta.patrimonio, "SEM_PATRIMONIO")
        self.assertEqual(ferramenta.valor_aquisicao, Decimal("1250.75"))

    def test_cadastro_exibe_locais_customizados_existentes(self):
        Ferramenta.objects.create(nome="Furadeira", local="OFICINA CENTRAL")

        client = Client()
        client.force_login(self.user)

        response = client.get("/ptmdsa/cadferramentas/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="OFICINA CENTRAL">OFICINA CENTRAL</option>')

    def test_novo_local_fica_disponivel_para_cadastros_posteriores(self):
        client = Client()
        client.force_login(self.user)

        response = client.post(
            "/ptmdsa/cadferramentas/cadastrar/",
            {"nome": "Furadeira", "local": "NOVO_LOCAL", "local_novo": "ALMOXARIFADO"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(LocalFerramenta.objects.filter(nome="ALMOXARIFADO").exists())

        response = client.get("/ptmdsa/cadferramentas/")
        self.assertContains(response, 'value="ALMOXARIFADO">ALMOXARIFADO</option>')

    def test_local_sem_uso_pode_ser_excluido(self):
        local = LocalFerramenta.objects.create(nome="LOCAL TEMPORARIO")
        client = Client()
        client.force_login(self.user)

        response = client.post(f"/ptmdsa/cadferramentas/locais/excluir/{local.id}/")

        self.assertEqual(response.status_code, 302)
        self.assertFalse(LocalFerramenta.objects.filter(id=local.id).exists())

    def test_local_em_uso_nao_pode_ser_excluido(self):
        ferramenta = Ferramenta.objects.create(nome="Furadeira", local="OFICINA")
        local = LocalFerramenta.objects.get(nome="OFICINA")
        client = Client()
        client.force_login(self.user)

        response = client.post(f"/ptmdsa/cadferramentas/locais/excluir/{local.id}/")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(LocalFerramenta.objects.filter(id=local.id).exists())
        self.assertTrue(Ferramenta.objects.filter(id=ferramenta.id).exists())

    def test_listagem_filtra_ferramentas_por_nome(self):
        Ferramenta.objects.create(nome="Furadeira Bosch", local="COFEN")
        Ferramenta.objects.create(nome="Alicate Universal", local="COFEN")

        client = Client()
        client.force_login(self.user)
        response = client.get(
            "/ptmdsa/cadferramentas/listar_ferramentas/",
            {"nome": "bosch"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Furadeira Bosch")
        self.assertNotContains(response, "Alicate Universal")

    def test_listagem_gera_dados_do_grafico_para_locais_personalizados(self):
        Ferramenta.objects.create(nome="Furadeira", local="OFICINA CENTRAL")
        Ferramenta.objects.create(nome="Alicate", local="OFICINA CENTRAL")

        client = Client()
        client.force_login(self.user)
        response = client.get("/ptmdsa/cadferramentas/listar_ferramentas/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            {"local": "OFICINA CENTRAL", "total": 2},
            response.context["por_local"],
        )
        self.assertContains(response, '<p>OFICINA CENTRAL</p>')

    def test_detalhes_ferramenta_exibe_informacoes_cadastradas(self):
        ferramenta = Ferramenta.objects.create(
            nome="Furadeira",
            local="OFICINA CENTRAL",
            patrimonio="PAT-123",
            descricao="Furadeira de bancada",
        )

        client = Client()
        client.force_login(self.user)

        response = client.get(f"/ptmdsa/cadferramentas/detalhes/{ferramenta.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Furadeira")
        self.assertContains(response, "OFICINA CENTRAL")
        self.assertContains(response, "Furadeira de bancada")

    def test_historico_e_registrado_ao_editar_ferramenta(self):
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        ferramenta = Ferramenta.objects.create(
            codigo="DSAFM-0001",
            patrimonio="SEM_PATRIMONIO",
            categoria="MANUAL",
            fabricante="ACME",
            nome="Chave de Fenda",
            data_aquisicao="2024-01-15",
            estado="NOVO",
            local="COFEN",
            descricao="Ferramenta de teste",
        )

        client = Client()
        client.force_login(self.user)

        response = client.post(
            f"/ptmdsa/cadferramentas/editar/{ferramenta.id}/",
            {
                "patrimonio": "PATR-123",
                "categoria": "MANUAL",
                "fabricante": "ACME",
                "nome": "Chave de Fenda XL",
                "data_aquisicao": "2024-01-15",
                "estado": "USADO",
                "local": "COFEN",
                "descricao": "Ferramenta de teste atualizada",
                "observacao": "Atualização de teste",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ferramenta.historicos.exists())
        self.assertIn("nome", [h.campo for h in ferramenta.historicos.all()])

    def test_editar_ferramenta_atualiza_responsavel(self):
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        servidor = Servidor.objects.create(
            matricula="DSAF0099",
            nome="Responsável Teste",
            cpf="999.999.999-99",
            rg="9999999",
            data_nascimento="1990-01-01",
            email="responsavel@example.com",
            telefone="61999999999",
            cep="70000-000",
            endereco="Rua Teste",
            bairro="Centro",
            cidade="Brasília",
            uf="DF",
        )
        ferramenta = Ferramenta.objects.create(
            codigo="DSAFM-0003",
            patrimonio="SEM_PATRIMONIO",
            categoria="MANUAL",
            fabricante="ACME",
            nome="Chave",
            estado="NOVO",
            local="COFEN",
        )

        client = Client()
        client.force_login(self.user)
        response = client.post(
            f"/ptmdsa/cadferramentas/editar/{ferramenta.id}/",
            {"responsavel": str(servidor.id), "nome": ferramenta.nome},
        )

        self.assertEqual(response.status_code, 302)
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.responsavel_id, servidor.id)

    def test_cadastrar_ferramenta_salva_fotos(self):
        client = Client()
        client.force_login(self.user)
        foto = SimpleUploadedFile(
            "ferramenta.jpg", b"fake-image-content", content_type="image/jpeg"
        )

        response = client.post(
            "/ptmdsa/cadferramentas/cadastrar_ferramenta/",
            {"nome": "Alicate", "fotos": foto},
        )

        self.assertEqual(response.status_code, 302)
        ferramenta = Ferramenta.objects.latest("id")
        self.assertEqual(
            FotoFerramenta.objects.filter(ferramenta=ferramenta).count(), 1
        )

    def test_cadastrar_ferramenta_salva_no_maximo_quatro_fotos(self):
        client = Client()
        client.force_login(self.user)
        fotos = [
            SimpleUploadedFile(
                f"ferramenta-{numero}.jpg",
                b"fake-image-content",
                content_type="image/jpeg",
            )
            for numero in range(5)
        ]

        response = client.post(
            "/ptmdsa/cadferramentas/cadastrar_ferramenta/",
            {"nome": "Alicate", "fotos": fotos},
        )

        self.assertEqual(response.status_code, 302)
        ferramenta = Ferramenta.objects.latest("id")
        self.assertEqual(
            FotoFerramenta.objects.filter(ferramenta=ferramenta).count(), 4
        )

    def test_editar_ferramenta_adiciona_fotos(self):
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        ferramenta = Ferramenta.objects.create(nome="Chave", local="COFEN")
        foto = SimpleUploadedFile(
            "nova-foto.jpg", b"fake-image-content", content_type="image/jpeg"
        )
        client = Client()
        client.force_login(self.user)

        response = client.post(
            f"/ptmdsa/cadferramentas/editar/{ferramenta.id}/",
            {"nome": ferramenta.nome, "fotos": foto},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(FotoFerramenta.objects.filter(ferramenta=ferramenta).exists())

    def test_usuario_comum_solicita_alteracao_e_administrador_aprova(self):
        ferramenta = Ferramenta.objects.create(nome="Chave", local="COFEN")
        client = Client()
        client.force_login(self.user)
        response = client.post(
            f"/ptmdsa/cadferramentas/editar/{ferramenta.id}/",
            {"nome": "Chave Atualizada", "local": "COFEN"},
        )

        self.assertEqual(response.status_code, 302)
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.nome, "Chave")
        solicitacao = SolicitacaoAlteracao.objects.get(objeto_id=ferramenta.id)
        self.assertEqual(solicitacao.status, SolicitacaoAlteracao.STATUS_PENDENTE)

        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        response = client.post(
            f"/ptmdsa/solicitacoes/{solicitacao.id}/avaliar/",
            {"decisao": "aprovar"},
        )

        self.assertEqual(response.status_code, 302)
        ferramenta.refresh_from_db()
        solicitacao.refresh_from_db()
        self.assertEqual(ferramenta.nome, "Chave Atualizada")
        self.assertEqual(solicitacao.status, SolicitacaoAlteracao.STATUS_APROVADA)

    def test_excluir_ferramenta_remove_registro(self):
        ferramenta = Ferramenta.objects.create(
            codigo="DSAFM-0002",
            patrimonio="SEM_PATRIMONIO",
            categoria="MANUAL",
            fabricante="ACME",
            nome="Furadeira",
            estado="NOVO",
            local="COFEN",
        )

        client = Client()
        client.force_login(self.user)

        response = client.post(f"/ptmdsa/cadferramentas/excluir/{ferramenta.id}/")

        self.assertRedirects(response, "/ptmdsa/cadferramentas/listar_ferramentas/")
        self.assertFalse(Ferramenta.objects.filter(id=ferramenta.id).exists())

    def test_relatorio_filtra_por_responsavel_e_historico(self):
        servidor = Servidor.objects.create(
            matricula="DSAF0100",
            nome="Responsável Relatório",
            cpf="888.888.888-88",
            rg="8888888",
            data_nascimento="1990-01-01",
            email="relatorio@example.com",
            telefone="61999999999",
            cep="70000-000",
            endereco="Rua Teste",
            bairro="Centro",
            cidade="Brasília",
            uf="DF",
        )
        ferramenta = Ferramenta.objects.create(
            codigo="DSAFM-0004",
            nome="Relatório Teste",
            categoria="MANUAL",
            local="COFEN",
            responsavel=servidor,
        )
        ferramenta.historicos.create(campo="nome", valor_novo="alterado")

        client = Client()
        client.force_login(self.user)
        response = client.get(
            "/ptmdsa/cadferramentas/relatorio/",
            {"responsavel": servidor.id, "historico": "sim"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ferramenta.codigo)
