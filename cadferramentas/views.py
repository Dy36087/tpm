from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Ferramenta, HistoricoAlteracaoFerramenta
from django.shortcuts import get_object_or_404
from pontoele.models import Servidor
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count

try:
    from openpyxl import Workbook
except ImportError:  # pragma: no cover - dependência opcional
    Workbook = None

try:
    from reportlab.pdfgen import canvas
except ImportError:  # pragma: no cover - dependência opcional
    canvas = None


# Create your views here.


@login_required
def dashboard_ferramentas(request):

    total_ferramentas = Ferramenta.objects.count()

    total_cofen = Ferramenta.objects.filter(local="COFEN").count()

    total_caesb = Ferramenta.objects.filter(local="CAESB").count()

    por_categoria = Ferramenta.objects.values("categoria").annotate(total=Count("id"))

    por_local = Ferramenta.objects.values("local").annotate(total=Count("id"))

    return render(
        request,
        "dashboard_ferramentas.html",
        {
            "total_ferramentas": total_ferramentas,
            "total_cofen": total_cofen,
            "total_caesb": total_caesb,
            "por_categoria": list(por_categoria),
            "por_local": list(por_local),
        },
    )


@login_required
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


@login_required
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


@login_required
def cadferramentas(request):

    servidores = Servidor.objects.all().order_by("nome")

    return render(request, "cadferramentas.html", {"servidores": servidores})


@login_required
def listar_ferramentas(request):

    ferramentas = Ferramenta.objects.all().order_by("codigo")
    por_local = list(Ferramenta.objects.values("local").annotate(total=Count("id")))

    por_local = request.GET.get("local")
    categoria = request.GET.get("categoria")

    if por_local:
        ferramentas = ferramentas.filter(local=por_local)

    if categoria:
        ferramentas = ferramentas.filter(categoria=categoria)

    paginator = Paginator(ferramentas, 12)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "listarferramentas.html",
        {
            "page_obj": page_obj,
            "local_selecionado": por_local,
            "categoria_selecionada": categoria,
        },
    )


@login_required
def cadastrar_ferramenta(request):
    if request.method == "POST":
        possui_patrimonio = request.POST.get("possui_patrimonio")
        patrimonio = "SEM_PATRIMONIO"
        categoria = ""
        fabricante = ""
        nome = ""
        data_aquisicao = ""
        estado = ""
        local = ""
        descricao = ""
        responsavel = None

        if possui_patrimonio != "nao":
            patrimonio = request.POST.get("patrimonio", "").strip().upper()
            categoria = request.POST.get("categoria", "").strip().upper()
            fabricante = request.POST.get("fabricante", "").strip().upper()
            nome = request.POST.get("nome", "").strip().upper()
            data_aquisicao = request.POST.get("data_aquisicao", "").strip().upper()
            estado = request.POST.get("estado", "").strip().upper()
            local = request.POST.get("local", "").strip().upper()
            descricao = request.POST.get("descricao", "").strip().upper()
            responsavel_id = request.POST.get("responsavel", "").strip()
            if responsavel_id:
                responsavel = Servidor.objects.filter(id=responsavel_id).first()

        ferramenta = Ferramenta(
            patrimonio=patrimonio,
            categoria=categoria,
            fabricante=fabricante,
            nome=nome,
            data_aquisicao=data_aquisicao if data_aquisicao else None,
            estado=estado,
            local=local,
            descricao=descricao,
            responsavel=responsavel,
        )
        ferramenta.save()
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
        "patrimonio",
        "categoria",
        "fabricante",
        "nome",
        "data_aquisicao",
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


@login_required
def historico_ferramenta(request, id):
    ferramenta = get_object_or_404(Ferramenta, id=id)
    historico = ferramenta.historicos.select_related("usuario").all()
    return render(
        request,
        "historico_ferramenta.html",
        {"ferramenta": ferramenta, "historico": historico},
    )


@login_required
def editar_ferramenta(request, id):

    ferramenta = get_object_or_404(Ferramenta, id=id)

    if request.method == "POST":
        valores_anteriores = {
            campo: _normalizar_valor_historico(getattr(ferramenta, campo))
            for campo in [
                "patrimonio",
                "categoria",
                "fabricante",
                "nome",
                "data_aquisicao",
                "estado",
                "local",
                "descricao",
                "observacao",
            ]
        }

        dados_novos = {
            "patrimonio": request.POST.get("patrimonio", ""),
            "nome": request.POST.get("nome", ""),
            "categoria": request.POST.get("categoria", ""),
            "fabricante": request.POST.get("fabricante", ""),
            "data_aquisicao": request.POST.get("data_aquisicao") or None,
            "estado": request.POST.get("estado", ""),
            "local": request.POST.get("local", ""),
            "descricao": request.POST.get("descricao", ""),
            "observacao": request.POST.get("observacao", ""),
        }

        _registrar_historico_ferramenta(ferramenta, dados_novos, request.user)

        ferramenta.patrimonio = dados_novos["patrimonio"]
        ferramenta.nome = dados_novos["nome"]
        ferramenta.categoria = dados_novos["categoria"]
        ferramenta.fabricante = dados_novos["fabricante"]
        ferramenta.data_aquisicao = dados_novos["data_aquisicao"]
        ferramenta.estado = dados_novos["estado"]
        ferramenta.local = dados_novos["local"]
        ferramenta.descricao = dados_novos["descricao"]
        ferramenta.observacao = dados_novos["observacao"]

        ferramenta.save()

        return redirect("listar_ferramentas")

    return render(request, "editferramenta.html", {"ferramenta": ferramenta})
