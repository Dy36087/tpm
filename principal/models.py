from django.db import models
from django.conf import settings

# Create your models here.


class SolicitacaoAlteracao(models.Model):
	STATUS_PENDENTE = "pendente"
	STATUS_APROVADA = "aprovada"
	STATUS_REJEITADA = "rejeitada"
	STATUS_CHOICES = [
		(STATUS_PENDENTE, "Pendente"),
		(STATUS_APROVADA, "Aprovada"),
		(STATUS_REJEITADA, "Rejeitada"),
	]

	TIPO_FERRAMENTA = "ferramenta"
	TIPO_PATRIMONIO = "patrimonio"
	TIPO_SERVIDOR = "servidor"
	TIPO_CHOICES = [
		(TIPO_FERRAMENTA, "Ferramenta"),
		(TIPO_PATRIMONIO, "Patrimônio"),
		(TIPO_SERVIDOR, "Servidor"),
	]

	tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
	objeto_id = models.PositiveIntegerField()
	dados = models.JSONField()
	solicitante = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		related_name="solicitacoes_alteracao",
	)
	avaliador = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="solicitacoes_avaliadas",
	)
	status = models.CharField(
		max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDENTE
	)
	observacao_avaliacao = models.TextField(blank=True)
	criada_em = models.DateTimeField(auto_now_add=True)
	avaliada_em = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-criada_em"]

	def __str__(self):
		return f"{self.get_tipo_display()} #{self.objeto_id} - {self.get_status_display()}"
