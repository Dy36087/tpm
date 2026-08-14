from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .models import Patrimonio


class HistoricoPatrimonioTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="adminhist",
            email="adminhist@example.com",
            password="admin123",
        )

    def test_historico_e_registrado_ao_editar_item(self):
        item = Patrimonio.objects.create(
            tipo="proprio",
            codigo="COD-001",
            material="PINO",
            destino="estoque",
            estado_conservacao="novo",
            quantidade="2",
            valor="25.00",
            data_aquisicao="2024-01-15",
            localizacao="ALMOXARIFADO",
            status="ativo",
        )

        client = Client()
        client.force_login(self.user)

        response = client.post(
            f"/ptmdsa/cadptm/editar_item/{item.id}/",
            {
                "tipo": "proprio",
                "codigo": "COD-001",
                "material": "PINO A",
                "destino": "estoque",
                "estado_conservacao": "usado",
                "quantidade": "3",
                "valor": "35.00",
                "data_aquisicao": "2024-01-15",
                "localizacao": "ALMOXARIFADO B",
                "status": "ativo",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(item.historicos.exists())
        self.assertIn("material", [h.campo for h in item.historicos.all()])
