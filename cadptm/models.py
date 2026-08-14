from django.db import models, transaction
import uuid
from datetime import datetime
from io import BytesIO
from django.core.files.base import ContentFile

try:
    import qrcode
except ImportError:  # pragma: no cover
    qrcode = None


class SequenciaPatrimonio(models.Model):
    ano = models.IntegerField(unique=True)
    ultimo_numero = models.IntegerField(default=0)

    class Meta:
        app_label = "cadptm"


class Auditoria(models.Model):
    usuario = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    acao = models.CharField(max_length=50)
    tabela = models.CharField(max_length=50)
    registro_id = models.IntegerField()
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "cadptm"


class HistoricoAlteracaoPatrimonio(models.Model):
    item = models.ForeignKey(
        "Patrimonio",
        on_delete=models.CASCADE,
        related_name="historicos",
    )
    campo = models.CharField(max_length=100)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_novo = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historicos_patrimonio",
    )
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "cadptm"
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.item.patrimonio} - {self.campo}"


class Patrimonio(models.Model):
    TIPO = [
        ("proprio", "Proprio"),
        ("terceiro", "Terceiro"),
    ]

    ESTADO_CHOICES = [
        ("novo", "Novo"),
        ("usado", "Usado"),
        ("ruim", "Ruim"),
        ("defeito", "Defeito"),
        ("velho", "Velho"),
    ]

    DESTINO_CHOICES = [
        ("estoque", "Estoque"),
        ("usando", "Em Uso"),
        ("manutencao", "Manutenção"),
        ("baixado", "Baixado"),
    ]

    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("baixa", "Baixa"),
        ("emprestimo", "Empréstimo"),
        ("transferencia", "Transferência"),
    ]

    controle = models.CharField(max_length=50, unique=True, editable=False)
    patrimonio = models.CharField(max_length=50, unique=True, editable=False)

    tipo = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    estado_conservacao = models.CharField(max_length=20)
    quantidade = models.CharField(max_length=100)
    valor = models.CharField(max_length=100)
    data_aquisicao = models.DateField()
    localizacao = models.CharField(max_length=100)
    status = models.CharField(max_length=20)

    qr_code = models.ImageField(upload_to="qrcodes/", blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def gerar_qrcode(self):
        if qrcode is None:
            return

        data = f"{self.patrimonio}|{self.material}"

        img = qrcode.make(data)

        buffer = BytesIO()
        img.save(buffer, format="PNG")

        self.qr_code.save(
            f"{self.patrimonio}.png", ContentFile(buffer.getvalue()), save=False
        )

    def save(self, *args, **kwargs):

        # ✅ GERAR CONTROLE
        if not self.controle:
            self.controle = str(uuid.uuid4())[:8].upper()

        # ✅ GERAR PATRIMÔNIO ERP
        if not self.patrimonio:
            ano = datetime.now().year

            with transaction.atomic():
                seq, _ = SequenciaPatrimonio.objects.select_for_update().get_or_create(
                    ano=ano
                )
                seq.ultimo_numero += 1
                seq.save()

                self.patrimonio = f"DSA-{ano}-{seq.ultimo_numero:05d}"

        # ✅ salvar primeiro
        super().save(*args, **kwargs)

        # ✅ gerar QR depois
        if not self.qr_code:
            self.gerar_qrcode()
            super().save(update_fields=["qr_code"])

    class Meta:
        app_label = "cadptm"

    def __str__(self):
        return self.patrimonio
