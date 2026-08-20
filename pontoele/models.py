from django.db import models

# Create your models here.


class Servidor(models.Model):

    matricula = models.CharField(max_length=8, unique=True)

    nome = models.CharField(max_length=200)

    cpf = models.CharField(max_length=14, unique=True)

    rg = models.CharField(max_length=20)

    data_nascimento = models.DateField()

    email = models.EmailField()

    telefone = models.CharField(max_length=20)

    endereco = models.CharField(max_length=300)

    bairro = models.CharField(max_length=100)

    cidade = models.CharField(max_length=100)

    uf = models.CharField(max_length=2)

    cep = models.CharField(max_length=9)

    face_encoding = models.JSONField(null=True, blank=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pontoele_servidor"

    def __str__(self):

        return f"{self.matricula} - " f"{self.nome}"


class RegistroPonto(models.Model):

    TIPOS = [
        ("entrada", "Entrada Trabalho"),
        ("saida_pausa", "Saída Pausa"),
        ("retorno_pausa", "Retorno Pausa"),
        ("saida", "Saída Trabalho"),
    ]

    servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE)

    tipo = models.CharField(max_length=20, choices=TIPOS)

    data_hora = models.DateTimeField(auto_now_add=True)

    latitude = models.FloatField()

    longitude = models.FloatField()
