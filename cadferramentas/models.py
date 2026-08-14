from django.conf import settings
from django.db import models
from pontoele.models import Servidor

# Create your models here.


class HistoricoAlteracaoFerramenta(models.Model):
    ferramenta = models.ForeignKey(
        "Ferramenta",
        on_delete=models.CASCADE,
        related_name="historicos",
    )
    campo = models.CharField(max_length=100)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_novo = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historicos_ferramentas",
    )
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.ferramenta.codigo} - {self.campo}"


class Ferramenta(models.Model):
    codigo = models.CharField(max_length=16, unique=True, blank=True, default="")
    patrimonio = models.CharField(max_length=100, blank=True)
    categoria = models.CharField(max_length=50, blank=True)
    fabricante = models.CharField(max_length=100, blank=True)
    nome = models.CharField(max_length=100)
    data_aquisicao = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True)
    local = models.CharField(max_length=100, blank=True)
    descricao = models.TextField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    responsavel = models.ForeignKey(
        "pontoele.Servidor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ferramenta",
    )

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._next_codigo()
        super().save(*args, **kwargs)

    @classmethod
    def _next_codigo(cls):
        last = cls.objects.filter(codigo__startswith="DSAFM-").order_by("-id").first()
        if last and last.codigo:
            try:
                last_number = int(last.codigo.split("-")[-1])
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0
        return f"DSAFM-{last_number + 1:04d}"

    def __str__(self):
        return self.nome
