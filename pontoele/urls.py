from django.urls import path
from . import views

urlpatterns = [
    path("", views.pontoeleptm, name="pontoeleptm"),
    path("cadfaceptm/", views.cadfaceptm, name="cadfaceptm"),
    path("cadastrar-face/", views.cadastrar_face, name="cadastrar_face"),
    path("registrar-ponto/", views.registrar_ponto, name="registrar_ponto"),
    path("servidores/", views.listar_servidores, name="listar_servidores"),
    path("usersfaceptm/", views.usersfaceptm, name="usersfaceptm"),
]
