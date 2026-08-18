from importlib import import_module

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase

from .models import Ferramenta


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
