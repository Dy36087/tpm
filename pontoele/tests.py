import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Servidor


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
        usuario = get_user_model().objects.create_user(
            username="gestor", password="senha-segura"
        )
        self.client.force_login(usuario)
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
