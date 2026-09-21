from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import SolicitacaoAlteracao
from .access import usuario_administrador


def criar_solicitacao_alteracao(tipo, objeto_id, dados, usuario):
    return SolicitacaoAlteracao.objects.create(
        tipo=tipo,
        objeto_id=objeto_id,
        dados=dados,
        solicitante=usuario,
    )


def index(request):
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    return render(request, "ptm.html")


@login_required
def ptmprincipal(request):
    return render(request, "ptm.html")


@login_required
def listar_solicitacoes(request):
    if not usuario_administrador(request.user):
        return HttpResponseForbidden("Apenas administradores podem avaliar solicitações.")
    return render(
        request,
        "solicitacoes_alteracao.html",
        {"solicitacoes": SolicitacaoAlteracao.objects.select_related("solicitante")},
    )


@login_required
def avaliar_solicitacao(request, id):
    if not usuario_administrador(request.user):
        return HttpResponseForbidden("Apenas administradores podem avaliar solicitações.")
    solicitacao = get_object_or_404(
        SolicitacaoAlteracao.objects.select_related("solicitante"), id=id
    )
    if request.method != "POST" or solicitacao.status != SolicitacaoAlteracao.STATUS_PENDENTE:
        return redirect("listar_solicitacoes")

    decisao = request.POST.get("decisao")
    if decisao not in {"aprovar", "rejeitar"}:
        return redirect("listar_solicitacoes")

    if decisao == "aprovar":
        from cadferramentas.models import Ferramenta
        from cadptm.models import Patrimonio
        from pontoele.models import Servidor

        dados = solicitacao.dados
        modelos = {
            SolicitacaoAlteracao.TIPO_FERRAMENTA: Ferramenta,
            SolicitacaoAlteracao.TIPO_PATRIMONIO: Patrimonio,
            SolicitacaoAlteracao.TIPO_SERVIDOR: Servidor,
        }
        objeto = modelos[solicitacao.tipo].objects.get(id=solicitacao.objeto_id)
        for campo, valor in dados.items():
            if campo == "responsavel_id":
                setattr(objeto, "responsavel_id", valor or None)
            else:
                setattr(objeto, campo, valor)
        objeto.save()
        solicitacao.status = SolicitacaoAlteracao.STATUS_APROVADA
        messages.success(request, "Solicitação aprovada e alteração aplicada.")
    else:
        solicitacao.status = SolicitacaoAlteracao.STATUS_REJEITADA
        messages.info(request, "Solicitação rejeitada.")

    solicitacao.avaliador = request.user
    solicitacao.avaliada_em = timezone.now()
    solicitacao.observacao_avaliacao = request.POST.get("observacao", "").strip()
    solicitacao.save()
    return redirect("listar_solicitacoes")
