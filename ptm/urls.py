from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from principal import views as principal_views

urlpatterns = [
    path("", principal_views.index, name="home"),
    path("admin/", admin.site.urls),
    path("ptmdsa/", include("principal.urls")),
    path("ptmdsa/cadptm/", include("cadptm.urls")),
    path("ptmdsa/pontoeleptm/", include("pontoele.urls")),
    path("ptmdsa/cadferramentas/", include("cadferramentas.urls")),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path(
        "senha/redefinir/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "senha/redefinir/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "senha/redefinir/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "senha/redefinir/concluido/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("ptmdsa/ptmservicos/", include("ptmservicos.urls")),
    path("ptmdsa/ptmorcamentos/", include("ptmorcamentos.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
