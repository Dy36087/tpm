from django.urls import path
from . import views

urlpatterns = [
    path("", views.cadferramentas, name="cadferramentas"),
    path("listar_ferramentas/", views.listar_ferramentas, name="listar_ferramentas"),
    path(
        "cadastrar_ferramenta/", views.cadastrar_ferramenta, name="cadastrar_ferramenta"
    ),
    path("editar/<int:id>/", views.editar_ferramenta, name="editar_ferramenta"),
    path(
        "historico/<int:id>/", views.historico_ferramenta, name="historico_ferramenta"
    ),
    path(
        "exportar/excel/",
        views.exportar_ferramentas_excel,
        name="exportar_ferramentas_excel",
    ),
    path(
        "exportar/pdf/", views.exportar_ferramentas_pdf, name="exportar_ferramentas_pdf"
    ),
    path("dashboard/", views.dashboard_ferramentas, name="dashboard_ferramentas"),
]
