from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden

NIVEIS_ACESSO = {
    "pontoele": "Ponto Eletrônico",
    "patrimonio": "Patrimônio",
    "ferramentas": "Ferramentas",
}
NIVEL_ADMINISTRADOR = "Administrador"


def grupos_de_acesso():
    nomes = [NIVEL_ADMINISTRADOR, *NIVEIS_ACESSO.values()]
    grupos = {}
    for nome in nomes:
        grupos[nome], _ = Group.objects.get_or_create(name=nome)
    return grupos


def usuario_administrador(usuario):
    return (
        usuario.is_superuser
        or usuario.is_staff
        or usuario.groups.filter(name=NIVEL_ADMINISTRADOR).exists()
    )


def nivel_acesso(nivel):
    nome_grupo = NIVEIS_ACESSO[nivel]

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if (
                usuario_administrador(request.user)
                or request.user.groups.filter(name=nome_grupo).exists()
            ):
                return view(request, *args, **kwargs)
            return HttpResponseForbidden("Você não possui acesso a este módulo.")

        return wrapped

    return decorator
