from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from smtplib import SMTPException
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from principal.access import (
    NIVEIS_ACESSO,
    NIVEL_ADMINISTRADOR,
    grupos_de_acesso,
    nivel_acesso,
    usuario_administrador,
)
from principal.views import criar_solicitacao_alteracao
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RegistroPonto, Servidor
from .models import Servidor
from .models import RegistroPonto
from math import radians
from math import sin
from math import cos
from math import sqrt
from math import atan2
import json

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


class UsuarioCreationForm(UserCreationForm):
    email = forms.EmailField(required=False, label="E-mail")

    class Meta:
        model = User
        fields = ("username", "email")


# Create your views here.
def gerar_matricula():

    ultimo = Servidor.objects.order_by("-id").first()

    if ultimo:

        numero = int(ultimo.matricula[4:]) + 1

    else:
        numero = 1

    return f"DSAF{numero:04d}"


@nivel_acesso("pontoele")
def cadfaceptm(request):
    return render(request, "cadfaceptm.html")


@nivel_acesso("pontoele")
def pontoeleptm(request):
    return render(request, "pontoeleptm.html")


@nivel_acesso("pontoele")
def usersfaceptm(request):
    servidores = Servidor.objects.all()
    return render(request, "ptmcolaboradores.html", {"servidores": servidores})


@login_required
def cadastrar_usuario(request):
    if not usuario_administrador(request.user):
        return HttpResponseForbidden("Apenas administradores podem cadastrar usuários.")

    grupos = grupos_de_acesso()
    form = UsuarioCreationForm(request.POST or None)
    if form.is_valid():
        usuario = form.save()
        messages.success(request, f"Usuário {usuario.username} cadastrado com sucesso.")
        return redirect("cadastrar_usuario")

    usuarios = User.objects.prefetch_related("groups").order_by("username")
    for usuario in usuarios:
        usuario.niveis = [
            {
                "nome": nome,
                "id": grupo.id,
                "atributos": " checked" if grupo in usuario.groups.all() else "",
                "bloqueado": (
                    " disabled"
                    if usuario == request.user and nome == NIVEL_ADMINISTRADOR
                    else ""
                ),
            }
            for nome, grupo in grupos.items()
        ]
    return render(
        request,
        "cadastrar_usuario.html",
        {
            "form": form,
            "usuarios": usuarios,
            "niveis": list(grupos.items()),
        },
    )


@login_required
def atualizar_acessos_usuario(request, usuario_id):
    if not usuario_administrador(request.user):
        return HttpResponseForbidden("Apenas administradores podem alterar acessos.")
    if request.method != "POST":
        return redirect("cadastrar_usuario")

    usuario = get_object_or_404(User, id=usuario_id)
    email = request.POST.get("email", "").strip()
    try:
        usuario.email = forms.EmailField(required=False).clean(email)
    except forms.ValidationError:
        messages.error(request, "Informe um e-mail válido para o usuário.")
        return redirect("cadastrar_usuario")
    usuario.save(update_fields=["email"])
    grupos = grupos_de_acesso()
    for nome_grupo, grupo in grupos.items():
        if nome_grupo == NIVEL_ADMINISTRADOR and usuario == request.user:
            continue
        if request.POST.get(f"grupo_{grupo.id}"):
            usuario.groups.add(grupo)
        else:
            usuario.groups.remove(grupo)

    messages.success(request, f"Acessos de {usuario.username} atualizados.")
    return redirect("cadastrar_usuario")


@login_required
def enviar_link_redefinicao_senha(request):
    if not usuario_administrador(request.user):
        return HttpResponseForbidden("Apenas administradores podem redefinir senhas.")
    if request.method != "POST":
        return redirect("cadastrar_usuario")

    usuario = get_object_or_404(User, id=request.POST.get("usuario_id"))
    if not usuario.email:
        messages.error(
            request,
            f"O usuário {usuario.username} não possui e-mail cadastrado.",
        )
        return redirect("cadastrar_usuario")

    form = PasswordResetForm({"email": usuario.email})
    if not form.is_valid():
        messages.error(request, "O e-mail cadastrado não é válido.")
        return redirect("cadastrar_usuario")

    try:
        form.save(
            request=request,
            use_https=request.is_secure(),
            subject_template_name="registration/password_reset_subject.txt",
            email_template_name="registration/password_reset_email.html",
        )
    except (SMTPException, OSError):
        messages.error(
            request,
            "Não foi possível enviar o e-mail. Verifique a configuração SMTP.",
        )
    else:
        messages.success(
            request,
            f"Link para alteração de senha enviado para {usuario.email}.",
        )
    return redirect("cadastrar_usuario")


@csrf_exempt
@nivel_acesso("pontoele")
def cadastrar_face(request):
    if request.method != "POST":
        return JsonResponse(
            {"sucesso": False, "erro": "Método não permitido."}, status=405
        )

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"sucesso": False, "erro": "Dados do cadastro inválidos."}, status=400
        )

    campos_obrigatorios = [
        "nome",
        "cpf",
        "rg",
        "data_nascimento",
        "email",
        "telefone",
        "cep",
        "endereco",
        "bairro",
        "cidade",
        "uf",
    ]
    campos_ausentes = [campo for campo in campos_obrigatorios if not dados.get(campo)]
    if campos_ausentes:
        return JsonResponse(
            {"sucesso": False, "erro": "Preencha todos os campos obrigatórios."},
            status=400,
        )

    cep_numerico = "".join(
        caractere for caractere in dados["cep"] if caractere.isdigit()
    )
    if len(cep_numerico) != 8:
        return JsonResponse(
            {"sucesso": False, "erro": "Informe um CEP com 8 dígitos."},
            status=400,
        )

    try:
        servidor = Servidor(
            matricula=gerar_matricula(),
            nome=dados["nome"],
            cpf=dados["cpf"],
            rg=dados["rg"],
            data_nascimento=dados["data_nascimento"],
            email=dados["email"],
            telefone=dados["telefone"],
            cep=f"{cep_numerico[:5]}-{cep_numerico[5:]}",
            endereco=dados["endereco"],
            bairro=dados["bairro"],
            cidade=dados["cidade"],
            uf=dados["uf"],
            face_encoding=dados.get("face_encoding"),
        )
        servidor.full_clean()
        servidor.save()
    except ValidationError as erro:
        return JsonResponse({"sucesso": False, "erro": erro.message_dict}, status=400)
    except IntegrityError:
        return JsonResponse(
            {"sucesso": False, "erro": "CPF ou matrícula já cadastrados."},
            status=400,
        )

    return JsonResponse({"sucesso": True, "matricula": servidor.matricula})


def distancia_metros(lat1, lon1, lat2, lon2):

    R = 6371000

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)

    a = (
        sin(dLat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def validar_sequencia(servidor, tipo):

    ultimo = (
        RegistroPonto.objects.filter(servidor=servidor).order_by("-data_hora").first()
    )

    if ultimo is None:
        return tipo == "entrada"

    regras = {
        "entrada": "saida_pausa",
        "saida_pausa": "retorno_pausa",
        "retorno_pausa": "saida",
        "saida": "entrada",
    }

    return regras.get(ultimo.tipo) == tipo


@csrf_exempt
@nivel_acesso("pontoele")
def registrar_ponto(request):

    dados = json.loads(request.body)

    matricula = dados["matricula"]

    tipo = dados["tipoPonto"]

    foto = dados["foto"]

    latitude = float(dados["latitude"])

    longitude = float(dados["longitude"])

    servidor = Servidor.objects.get(matricula=matricula)

    # Reconhecimento facial

    encoding_atual = dados["face_encoding"]

    autorizado = validar_face(servidor.face_encoding, encoding_atual)

    if not autorizado:

        return JsonResponse({"autorizado": False, "erro": "Face não reconhecida"})

    # Geolocalização
    LOCAIS = {
        "entrada": {"lat": -15.794229, "lon": -47.882166, "raio": 100},
        "saida_pausa": {"lat": -15.794229, "lon": -47.882166, "raio": 100},
        "retorno_pausa": {"lat": -15.794229, "lon": -47.882166, "raio": 100},
        "saida": {"lat": -15.794229, "lon": -47.882166, "raio": 100},
    }

    local = LOCAIS[tipo]

    distancia = distancia_metros(latitude, longitude, local["lat"], local["lon"])

    if distancia > local["raio"]:

        return JsonResponse({"autorizado": False, "erro": "Fora do local autorizado"})

    # Sequência

    if not validar_sequencia(servidor, tipo):

        return JsonResponse(
            {"autorizado": False, "erro": "Sequência de ponto inválida"}
        )

    RegistroPonto.objects.create(
        servidor=servidor, tipo=tipo, latitude=latitude, longitude=longitude
    )

    return JsonResponse(
        {"autorizado": True, "mensagem": "Registro de ponto realizado com sucesso"}
    )


def validar_face(encoding_salvo, encoding_atual):
    if np is None:
        return False

    try:
        distancia = np.linalg.norm(np.array(encoding_salvo) - np.array(encoding_atual))
        return distancia < 0.45
    except Exception:
        return False


@nivel_acesso("pontoele")
def listar_servidores(request):

    pesquisa = request.GET.get("q", "")

    servidores = Servidor.objects.all()

    if pesquisa:

        servidores = servidores.filter(
            nome__icontains=pesquisa
        ) | Servidor.objects.filter(matricula__icontains=pesquisa)

    return render(
        request,
        "ptmcolaboradores.html",
        {"servidores": servidores, "pesquisa": pesquisa},
    )


@nivel_acesso("pontoele")
def editar_servidor(request, servidor_id):
    servidor = get_object_or_404(Servidor, id=servidor_id)
    if request.method == "POST":
        dados = {
            campo: request.POST.get(campo, "").strip()
            for campo in [
                "nome", "cpf", "rg", "data_nascimento", "email", "telefone",
                "cep", "endereco", "bairro", "cidade", "uf",
            ]
        }
        if not usuario_administrador(request.user):
            criar_solicitacao_alteracao("servidor", servidor.id, dados, request.user)
            messages.info(request, "Alteração enviada para avaliação do administrador.")
            return redirect("listar_servidores")
        for campo in [
            "nome",
            "cpf",
            "rg",
            "data_nascimento",
            "email",
            "telefone",
            "cep",
            "endereco",
            "bairro",
            "cidade",
            "uf",
        ]:
            setattr(servidor, campo, request.POST.get(campo, "").strip())

        cep_numerico = "".join(
            caractere for caractere in servidor.cep if caractere.isdigit()
        )
        if len(cep_numerico) == 8:
            servidor.cep = f"{cep_numerico[:5]}-{cep_numerico[5:]}"
        try:
            servidor.full_clean()
            servidor.save()
        except ValidationError:
            pass

    return redirect("listar_servidores")


@nivel_acesso("pontoele")
def excluir_servidor(request, servidor_id):
    if request.method == "POST":
        get_object_or_404(Servidor, id=servidor_id).delete()

    return redirect("listar_servidores")
