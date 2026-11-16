from django.urls import path
from . import views

urlpatterns = [
    path('', views.ptmorcamentosindex, name='ptmorcamentosindex'),
    path('novo/', views.ptmorcamentonovo, name='ptmorcamentonovo'),
]