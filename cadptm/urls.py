from django.urls import path
from . import views

urlpatterns = [
    path("", views.cadptm, name="cadptm"),
    path("pesquisar/", views.pesquisar, name="pesquisar"),
    path("pesquisar/listar_itens/<str:busca>/<str:status>/", views.listar_itens, name="listar_itens"),
    path("excluir_item/<int:id>/", views.excluir_item, name="excluir_item"),
    path("exportar/<str:formato>/<str:ids>/", views.exportar, name="exportar"),
    path("etiqueta/<int:id>/", views.etiqueta, name="etiqueta"),
    path("exportar/excel_etiqueta/ids/<str:ids>/", views.exportar, name="excel_etiqueta"),
]
