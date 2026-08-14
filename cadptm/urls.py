from django.urls import path
from . import views

urlpatterns = [
    path("", views.cadptm, name="cadptm"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("pesquisar/", views.pesquisar, name="pesquisar"),
    path(
        "pesquisar/listar_itens/<str:busca>/<str:status>/",
        views.listar_itens,
        name="listar_itens",
    ),
    path("excluir_item/<int:id>/", views.excluir_item, name="excluir_item"),
    path("editar_item/<int:id>/", views.editar_item, name="editar_item"),
    path("historico/<int:id>/", views.historico_item, name="historico_item"),
    path("exportar/<str:formato>/<str:ids>/", views.exportar, name="exportar"),
    path(
        "exportar_filtro/<str:formato>/<str:busca>/<str:status>/",
        views.exportar_filtro,
        name="exportar_filtro",
    ),
    path("etiqueta/<int:id>/", views.etiqueta, name="etiqueta"),
    path(
        "exportar/excel_etiqueta/ids/<str:ids>/", views.exportar, name="excel_etiqueta"
    ),
]
