from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render
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


# Create your views here.
def gerar_matricula():

    ultimo = Servidor.objects.order_by("-id").first()

    if ultimo:

        numero = int(ultimo.matricula[4:]) + 1

    else:
        numero = 1

    return f"DSAF{numero:04d}"


@login_required
def cadfaceptm(request):
    return render(request, "cadfaceptm.html")


@login_required
def pontoeleptm(request):
    return render(request, "pontoeleptm.html")


@login_required
def usersfaceptm(request):
    servidores = Servidor.objects.all()
    return render(request, "usersfaceptm.html", {"servidores": servidores})


@csrf_exempt
@login_required
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

    try:
        servidor = Servidor(
            matricula=gerar_matricula(),
            nome=dados["nome"],
            cpf=dados["cpf"],
            rg=dados["rg"],
            data_nascimento=dados["data_nascimento"],
            email=dados["email"],
            telefone=dados["telefone"],
            cep=dados["cep"],
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
@login_required
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


@login_required
def listar_servidores(request):

    pesquisa = request.GET.get("q", "")

    servidores = Servidor.objects.all()

    if pesquisa:

        servidores = servidores.filter(
            nome__icontains=pesquisa
        ) | Servidor.objects.filter(matricula__icontains=pesquisa)

    return render(
        request,
        "listar_servidores.html",
        {"servidores": servidores, "pesquisa": pesquisa},
    )
