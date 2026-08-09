from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from principal import views as principal_views

urlpatterns = [
    path("", principal_views.index, name="home"),
    path("admin/", admin.site.urls),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("ptmdsa/", include("principal.urls")),
    path("ptmdsa/cadptm/", include("cadptm.urls")),
    path("ptmdsa/pontoeleptm/", include("pontoele.urls")),
    path("ptmdsa/cadferramentas/", include("cadferramentas.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
