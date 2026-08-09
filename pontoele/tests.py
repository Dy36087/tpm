import json
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from .models import Servidor


class CadastrarFaceTests(TestCase):
    def test_cadastrar_face_salva_servidor_com_face_encoding(self):
        payload = {
            "nome": "Maria Souza",
            "face_encoding": [0.1, 0.2, 0.3],
        }

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


class TemplateCadastroTests(TestCase):
    def test_template_envia_o_encoding_da_detecao(self):
        template_path = Path(settings.BASE_DIR) / "pontoele/templates/cadfaceptm.html"
        content = template_path.read_text(encoding="utf-8")

        self.assertIn("resultadoDeteccao.faceEncoding", content)
