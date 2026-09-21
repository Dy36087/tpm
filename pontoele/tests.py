import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Servidor
from principal.access import grupos_de_acesso


class CadastrarFaceTests(TestCase):
    def test_cadastrar_face_salva_servidor_com_face_encoding(self):
        payload = {
            "nome": "Maria Souza",
            "cpf": "123.456.789-01",
            "rg": "1234567",
            "data_nascimento": "1990-01-01",
            "email": "maria@example.com",
            "telefone": "61999999999",
            "cep": "70000-000",
            "endereco": "Rua Teste",
            "bairro": "Centro",
            "cidade": "Brasília",
            "uf": "DF",
            "face_encoding": [0.1, 0.2, 0.3],
        }
        usuario = get_user_model().objects.create_user(
            username="operador", password="senha-segura"
        )
        usuario.groups.add(grupos_de_acesso()["Ponto Eletrônico"])
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("cadastrar_face"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["sucesso"])

        servidor = Servidor.objects.get(matricula=response.json()["matricula"])
        self.assertEqual(servidor.nome, "Maria Souza")
        self.assertEqual(servidor.face_encoding, [0.1, 0.2, 0.3])
        self.assertEqual(Servidor._meta.db_table, "pontoele_servidor")


class GerenciarServidorTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="gestor", password="senha-segura"
        )
        self.usuario.groups.add(grupos_de_acesso()["Ponto Eletrônico"])
        self.client.force_login(self.usuario)
        self.servidor = Servidor.objects.create(
            matricula="DSAF0001",
            nome="Maria Souza",
            cpf="123.456.789-01",
            rg="1234567",
            data_nascimento="1990-01-01",
            email="maria@example.com",
            telefone="61999999999",
            cep="70000-000",
            endereco="Rua Teste",
            bairro="Centro",
            cidade="Brasília",
            uf="DF",
        )

    def test_editar_servidor_atualiza_registro(self):
        self.usuario.is_staff = True
        self.usuario.save(update_fields=["is_staff"])
        response = self.client.post(
            reverse("editar_servidor", args=[self.servidor.id]),
            {
                "nome": "Maria Silva",
                "cpf": self.servidor.cpf,
                "rg": self.servidor.rg,
                "data_nascimento": "1990-01-01",
                "email": "maria.silva@example.com",
                "telefone": self.servidor.telefone,
                "cep": "70000000",
                "endereco": self.servidor.endereco,
                "bairro": self.servidor.bairro,
                "cidade": self.servidor.cidade,
                "uf": self.servidor.uf,
            },
        )

        self.assertRedirects(response, reverse("listar_servidores"))
        self.servidor.refresh_from_db()
        self.assertEqual(self.servidor.nome, "Maria Silva")
        self.assertEqual(self.servidor.cep, "70000-000")

    def test_excluir_servidor_remove_registro(self):
        response = self.client.post(
            reverse("excluir_servidor", args=[self.servidor.id])
        )

        self.assertRedirects(response, reverse("listar_servidores"))
        self.assertFalse(Servidor.objects.filter(id=self.servidor.id).exists())


class TemplateCadastroTests(TestCase):
    def test_template_envia_o_encoding_da_detecao(self):
        template_path = Path(settings.BASE_DIR) / "pontoele/templates/cadfaceptm.html"
        content = template_path.read_text(encoding="utf-8")

        self.assertIn("resultadoDeteccao.faceEncoding", content)


class CadastrarUsuarioTests(TestCase):
    def test_usuario_comum_nao_pode_cadastrar_usuario(self):
        usuario = get_user_model().objects.create_user(
            username="operador", password="senha-segura"
        )
        self.client.force_login(usuario)

        response = self.client.get(reverse("cadastrar_usuario"))

        self.assertEqual(response.status_code, 403)

    def test_staff_cadastra_usuario_com_senha_utilizavel(self):
        administrador = get_user_model().objects.create_user(
            username="administrador", password="senha-segura", is_staff=True
        )
        self.client.force_login(administrador)

        response = self.client.post(
            reverse("cadastrar_usuario"),
            {
                "username": "novo-usuario",
                "password1": "UmaSenhaForte123!",
                "password2": "UmaSenhaForte123!",
            },
        )

        self.assertRedirects(response, reverse("cadastrar_usuario"))
        novo_usuario = get_user_model().objects.get(username="novo-usuario")
        self.assertTrue(novo_usuario.check_password("UmaSenhaForte123!"))

    def test_tela_marca_nivel_que_usuario_possui(self):
        administrador = get_user_model().objects.create_user(
            username="administrador", password="senha-segura", is_staff=True
        )
        usuario = get_user_model().objects.create_user(
            username="patrimonio", password="senha-segura"
        )
        grupo = grupos_de_acesso()["Patrimônio"]
        usuario.groups.add(grupo)
        self.client.force_login(administrador)

        response = self.client.get(reverse("cadastrar_usuario"))

        self.assertContains(
            response,
            f'name="grupo_{grupo.id}" checked',
        )

    def test_staff_cadastra_usuario_com_email(self):
        administrador = get_user_model().objects.create_user(
            username="administrador", password="senha-segura", is_staff=True
        )
        self.client.force_login(administrador)

        response = self.client.post(
            reverse("cadastrar_usuario"),
            {
                "username": "usuario-com-email",
                "email": "usuario@example.com",
                "password1": "UmaSenhaForte123!",
                "password2": "UmaSenhaForte123!",
            },
        )

        self.assertRedirects(response, reverse("cadastrar_usuario"))
        usuario = get_user_model().objects.get(username="usuario-com-email")
        self.assertEqual(usuario.email, "usuario@example.com")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    def test_administrador_envia_link_para_usuario_selecionado(self):
        administrador = get_user_model().objects.create_user(
            username="administrador", password="senha-segura", is_staff=True
        )
        usuario = get_user_model().objects.create_user(
            username="patrimonio",
            password="senha-segura",
            email="patrimonio@example.com",
        )
        self.client.force_login(administrador)

        response = self.client.post(
            reverse("enviar_link_redefinicao_senha"),
            {"usuario_id": usuario.id},
        )

        self.assertRedirects(response, reverse("cadastrar_usuario"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/senha/redefinir/", mail.outbox[0].body)

    def test_usuario_comum_nao_pode_enviar_link_de_senha(self):
        usuario = get_user_model().objects.create_user(
            username="operador", password="senha-segura"
        )
        alvo = get_user_model().objects.create_user(
            username="patrimonio", email="patrimonio@example.com"
        )
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("enviar_link_redefinicao_senha"),
            {"usuario_id": alvo.id},
        )

        self.assertEqual(response.status_code, 403)
