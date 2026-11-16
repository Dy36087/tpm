from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import (
    FotoFerramenta,
    Ferramenta,
    HistoricoAlteracaoFerramenta,
)
from django.shortcuts import get_object_or_404
from pontoele.models import Servidor
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from principal.access import nivel_acesso, usuario_administrador
from principal.views import criar_solicitacao_alteracao
from ptmservicos.models import Cliente
from django.views.decorators.http import require_POST

try:
    from openpyxl import Workbook
except ImportError:  # pragma: no cover - dependência opcional
    Workbook = None

try:
    from reportlab.pdfgen import canvas
except ImportError:  # pragma: no cover - dependência opcional
    canvas = None


# Create your views here.


def locais_clientes(atual=""):
    nomes = sorted({nome.upper() for nome in Cliente.objects.values_list("nome", flat=True)})
    if atual and atual not in nomes:
        nomes.insert(0, atual)
    return nomes


def locais_com_totais(ferramentas):
    totais = {
        item["local"]: item["total"]
        for item in ferramentas.order_by().values("local").annotate(total=Count("id"))
    }
    return [
        {"local": nome, "total": totais.get(nome, 0)} for nome in locais_clientes()
    ]



@nivel_acesso("ferramentas")
def dashboard_ferramentas(request):

    total_ferramentas = Ferramenta.objects.count()

    por_categoria = Ferramenta.objects.values("categoria").annotate(total=Count("id"))

    por_local = locais_com_totais(Ferramenta.objects.all())

    return render(
        request,
        "dashboard_ferramentas.html",
        {
            "total_ferramentas": total_ferramentas,
            "por_categoria": list(por_categoria),
            "por_local": por_local,
        },
    )


@nivel_acesso("ferramentas")
def exportar_ferramentas_pdf(request):
    if canvas is None:
        return HttpResponse(
            "A dependência reportlab não está instalada.",
            status=500,
        )

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = "attachment; filename=ferramentas.pdf"

    pdf = canvas.Canvas(response)

    pdf.setTitle("Ferramentas")

    y = 800

    pdf.drawString(50, y, "RELAÇÃO DE FERRAMENTAS")

    y -= 30

    ferramentas = Ferramenta.objects.all()

    for ferramenta in ferramentas:

        linha = f"{ferramenta.codigo} | " f"{ferramenta.nome} | " f"{ferramenta.local}"

        pdf.drawString(50, y, linha)

        y -= 20

        if y <= 50:
            pdf.showPage()
            y = 800

    pdf.save()

    return response


@nivel_acesso("ferramentas")
def exportar_ferramentas_excel(request):
    if Workbook is None:
        return HttpResponse(
            "A dependência openpyxl não está instalada.",
            status=500,
        )

    wb = Workbook()
    ws = wb.active

    ws.title = "Ferramentas"

    cabecalho = [
        "Código",
        "Patrimônio",
        "Nome",
        "Categoria",
        "Fabricante",
        "Estado",
        "Local",
        "Responsável",
    ]

    ws.append(cabecalho)

    ferramentas = Ferramenta.objects.all()

    for ferramenta in ferramentas:

        ws.append(
            [
                ferramenta.codigo,
                ferramenta.patrimonio,
                ferramenta.nome,
                ferramenta.categoria,
                ferramenta.fabricante,
                ferramenta.estado,
                ferramenta.local,
                str(ferramenta.responsavel) if ferramenta.responsavel else "",
            ]
        )

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = "attachment; filename=ferramentas.xlsx"

    wb.save(response)

    return response


@nivel_acesso("ferramentas")
def cadferramentas(request):

    servidores = Servidor.objects.all().order_by("nome")

    return render(
        request,
        "cadferramentas.html",
        {
            "servidores": servidores,
            "locais": locais_clientes(),
        },
    )


@nivel_acesso("ferramentas")
def listar_ferramentas(request):

    ferramentas = Ferramenta.objects.all().order_by("codigo")
    nome_filtro = request.GET.get("nome", "").strip()
    local_filtro = request.GET.get("local")
    categoria = request.GET.get("categoria")

    if nome_filtro:
        ferramentas = ferramentas.filter(nome__icontains=nome_filtro)

    if local_filtro:
        ferramentas = ferramentas.filter(local=local_filtro)

    if categoria:
        ferramentas = ferramentas.filter(categoria=categoria)

    total_ferramentas = ferramentas.count()
    por_categoria = list(
        ferramentas.values("categoria")
        .annotate(total=Count("id"))
        .order_by("categoria")
    )
    por_local = locais_com_totais(ferramentas)

    paginator = Paginator(ferramentas, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "listarferramentas.html",
        {
            "page_obj": page_obj,
            "nome_filtro": nome_filtro,
            "local_selecionado": local_filtro,
            "locais": locais_clientes(local_filtro or ""),
            "categoria_selecionada": categoria,
            "total_ferramentas": total_ferramentas,
            "por_categoria": por_categoria,
            "por_local": por_local,
        },
    )


@nivel_acesso("ferramentas")
def relatorio_ferramentas(request):
    ferramenta_filtro = request.GET.get("ferramenta", "").strip()
    local_filtro = request.GET.get("local", "").strip()
    responsavel_filtro = request.GET.get("responsavel", "").strip()
    historico_filtro = request.GET.get("historico", "").strip()

    ferramentas = (
        Ferramenta.objects.select_related("responsavel")
        .prefetch_related("historicos__usuario")
        .order_by("codigo")
    )
    if ferramenta_filtro:
        ferramentas = ferramentas.filter(
            Q(nome__icontains=ferramenta_filtro)
            | Q(codigo__icontains=ferramenta_filtro)
            | Q(patrimonio__icontains=ferramenta_filtro)
        )
    if local_filtro:
        ferramentas = ferramentas.filter(local=local_filtro)
    if responsavel_filtro:
        ferramentas = ferramentas.filter(responsavel_id=responsavel_filtro)
    if historico_filtro == "sim":
        ferramentas = ferramentas.filter(historicos__isnull=False).distinct()
    elif historico_filtro == "nao":
        ferramentas = ferramentas.filter(historicos__isnull=True)

    return render(
        request,
        "relatorio_ferramentas.html",
        {
            "ferramentas": ferramentas,
            "servidores": Servidor.objects.all().order_by("nome"),
            "ferramenta_filtro": ferramenta_filtro,
            "local_filtro": local_filtro,
            "locais": locais_clientes(local_filtro),
            "responsavel_filtro": responsavel_filtro,
            "historico_filtro": historico_filtro,
        },
    )


@nivel_acesso("ferramentas")
def cadastrar_ferramenta(request):
    if request.method == "POST":
        possui_patrimonio = request.POST.get("possui_patrimonio", "sim").strip().lower()
        patrimonio = request.POST.get("patrimonio", "").strip().upper()
        categoria = request.POST.get("categoria", "").strip().upper()
        fabricante = request.POST.get("fabricante", "").strip().upper()
        nome = request.POST.get("nome", "").strip().upper()
        data_aquisicao = request.POST.get("data_aquisicao", "").strip()
        valor_aquisicao = request.POST.get("valor_aquisicao", "").strip()
        estado = request.POST.get("estado", "").strip().upper()
        local = request.POST.get("local", "").strip().upper()
        descricao = request.POST.get("descricao", "").strip().upper()
        responsavel = None

        if possui_patrimonio == "nao":
            patrimonio = "SEM_PATRIMONIO"
        elif not patrimonio:
            patrimonio = "SEM_PATRIMONIO"

        responsavel_id = request.POST.get("responsavel", "").strip()
        if responsavel_id:
            responsavel = Servidor.objects.filter(id=responsavel_id).first()

        ferramenta = Ferramenta(
            possui_patrimonio=possui_patrimonio,
            patrimonio=patrimonio,
            categoria=categoria,
            fabricante=fabricante,
            nome=nome,
            data_aquisicao=data_aquisicao if data_aquisicao else None,
            valor_aquisicao=valor_aquisicao if valor_aquisicao else None,
            estado=estado,
            local=local,
            descricao=descricao,
            responsavel=responsavel,
        )
        ferramenta.save()
        for imagem in request.FILES.getlist("fotos")[:4]:
            FotoFerramenta.objects.create(ferramenta=ferramenta, imagem=imagem)
        return redirect("cadferramentas")

    return render(request, "cadferramentas.html")


def _normalizar_valor_historico(valor):
    if valor is None:
        return ""
    if hasattr(valor, "isoformat"):
        return valor.isoformat()
    return str(valor)


def _registrar_historico_ferramenta(ferramenta, dados_novos, usuario):
    campos = [
        "possui_patrimonio",
        "patrimonio",
        "categoria",
        "fabricante",
        "nome",
        "data_aquisicao",
        "valor_aquisicao",
        "estado",
        "local",
        "descricao",
        "observacao",
    ]

    for campo in campos:
        valor_anterior = _normalizar_valor_historico(getattr(ferramenta, campo))
        valor_novo = _normalizar_valor_historico(dados_novos.get(campo))
        if valor_anterior != valor_novo:
            HistoricoAlteracaoFerramenta.objects.create(
                ferramenta=ferramenta,
                campo=campo,
                valor_anterior=valor_anterior,
                valor_novo=valor_novo,
                usuario=usuario,
            )


@nivel_acesso("ferramentas")
def historico_ferramenta(request, id):
    ferramenta = get_object_or_404(Ferramenta, id=id)
    historico = ferramenta.historicos.select_related("usuario").all()
    return render(
        request,
        "historico_ferramenta.html",
        {"ferramenta": ferramenta, "historico": historico},
    )


@nivel_acesso("ferramentas")
def detalhes_ferramenta(request, id):
    ferramenta = get_object_or_404(
        Ferramenta.objects.select_related("responsavel").prefetch_related("fotos"),
        id=id,
    )
    return render(request, "detalhes_ferramenta.html", {"ferramenta": ferramenta})


@nivel_acesso("ferramentas")
def editar_ferramenta(request, id):

    ferramenta = get_object_or_404(Ferramenta, id=id)

    if request.method == "POST":
        valores_anteriores = {
            campo: _normalizar_valor_historico(getattr(ferramenta, campo))
            for campo in [
                "possui_patrimonio",
                "patrimonio",
                "categoria",
                "fabricante",
                "nome",
                "data_aquisicao",
                "valor_aquisicao",
                "estado",
                "local",
                "descricao",
                "observacao",
                "responsavel",
            ]
        }

        possui_patrimonio = request.POST.get("possui_patrimonio", "sim").strip().lower()
        patrimonio = request.POST.get("patrimonio", "").strip().upper()
        valor_aquisicao = request.POST.get("valor_aquisicao", "").strip()

        if possui_patrimonio == "nao":
            patrimonio = "SEM_PATRIMONIO"
        elif not patrimonio:
            patrimonio = "SEM_PATRIMONIO"

        local = request.POST.get("local", "").strip().upper()

        responsavel_id = request.POST.get("responsavel", "").strip()
        responsavel = (
            Servidor.objects.filter(id=responsavel_id).first()
            if responsavel_id
            else None
        )

        dados_novos = {
            "possui_patrimonio": possui_patrimonio,
            "patrimonio": patrimonio,
            "nome": request.POST.get("nome", ""),
            "categoria": request.POST.get("categoria", ""),
            "fabricante": request.POST.get("fabricante", ""),
            "data_aquisicao": (
                request.POST.get("data_aquisicao", "").strip()
                or ferramenta.data_aquisicao
            ),
            "valor_aquisicao": valor_aquisicao or ferramenta.valor_aquisicao,
            "estado": request.POST.get("estado", ""),
            "local": local,
            "descricao": request.POST.get("descricao", ""),
            "observacao": request.POST.get("observacao", ""),
            "responsavel": responsavel,
        }

        if not usuario_administrador(request.user):
            criar_solicitacao_alteracao(
                "ferramenta",
                ferramenta.id,
                {
                    **{
                        campo: dados_novos[campo]
                        for campo in dados_novos
                        if campo != "responsavel"
                    },
                    "responsavel_id": responsavel.id if responsavel else None,
                },
                request.user,
            )
            messages.info(request, "Alteração enviada para avaliação do administrador.")
            return redirect("listar_ferramentas")

        _registrar_historico_ferramenta(ferramenta, dados_novos, request.user)

        ferramenta.possui_patrimonio = dados_novos["possui_patrimonio"]
        ferramenta.patrimonio = dados_novos["patrimonio"]
        ferramenta.nome = dados_novos["nome"]
        ferramenta.categoria = dados_novos["categoria"]
        ferramenta.fabricante = dados_novos["fabricante"]
        ferramenta.data_aquisicao = dados_novos["data_aquisicao"]
        ferramenta.valor_aquisicao = dados_novos["valor_aquisicao"]
        ferramenta.estado = dados_novos["estado"]
        ferramenta.local = dados_novos["local"]
        ferramenta.descricao = dados_novos["descricao"]
        ferramenta.observacao = dados_novos["observacao"]
        ferramenta.responsavel = dados_novos["responsavel"]

        ferramenta.save()
        for imagem in request.FILES.getlist("fotos")[:4]:
            FotoFerramenta.objects.create(ferramenta=ferramenta, imagem=imagem)

        return redirect("listar_ferramentas")

    return render(
        request,
        "editferramenta.html",
        {
            "ferramenta": ferramenta,
            "locais": locais_clientes(ferramenta.local),
            "servidores": Servidor.objects.all().order_by("nome"),
        },
    )


@nivel_acesso("ferramentas")
@require_POST
def excluir_ferramenta(request, id):
    ferramenta = get_object_or_404(Ferramenta, id=id)
    ferramenta.delete()
    return redirect("listar_ferramentas")
