from django.urls import path
from . import views

urlpatterns = [
    path("", views.pontoeleptm, name="pontoeleptm"),
    path("cadfaceptm/", views.cadfaceptm, name="cadfaceptm"),
    path("cadastrar-face/", views.cadastrar_face, name="cadastrar_face"),
    path("registrar-ponto/", views.registrar_ponto, name="registrar_ponto"),
    path("servidores/", views.listar_servidores, name="listar_servidores"),
    path(
        "servidores/<int:servidor_id>/editar/",
        views.editar_servidor,
        name="editar_servidor",
    ),
    path(
        "servidores/<int:servidor_id>/excluir/",
        views.excluir_servidor,
        name="excluir_servidor",
    ),
    path("usersfaceptm/", views.usersfaceptm, name="usersfaceptm"),
    path("cadastrar-usuario/", views.cadastrar_usuario, name="cadastrar_usuario"),
    path(
        "cadastrar-usuario/enviar-link-senha/",
        views.enviar_link_redefinicao_senha,
        name="enviar_link_redefinicao_senha",
    ),
    path(
        "cadastrar-usuario/<int:usuario_id>/acessos/",
        views.atualizar_acessos_usuario,
        name="atualizar_acessos_usuario",
    ),
]
