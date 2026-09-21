from django.urls import path

from . import views

urlpatterns = [
    path("", views.ptmprincipal, name="ptmprincipal"),
    path("solicitacoes/", views.listar_solicitacoes, name="listar_solicitacoes"),
    path(
        "solicitacoes/<int:id>/avaliar/",
        views.avaliar_solicitacao,
        name="avaliar_solicitacao",
    ),
]
