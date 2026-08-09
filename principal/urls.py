from django.urls import path

from . import views

urlpatterns = [
    path("", views.ptmprincipal, name="ptmprincipal"),
]
