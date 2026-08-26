from importlib import import_module

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase

from .models import Ferramenta
from principal.access import grupos_de_acesso
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

    def test_historico_e_registrado_ao_editar_ferramenta(self):
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
