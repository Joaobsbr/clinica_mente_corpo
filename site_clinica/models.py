from django.db import models
from django.contrib.auth.models import User

class Pacientes(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14)
    nome_social = models.CharField(max_length=100, blank=True)
    data_nascimento = models.DateField()
    profissao = models.CharField(max_length=70)
    escolaridade = models.CharField(max_length=30)
    telefone = models.CharField(max_length=20)
    email = models.TextField()
    cep = models.CharField(max_length=9)
    estado = models.CharField(max_length=50)
    cidade = models.CharField(max_length=50)
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    nome_resp = models.CharField(max_length=150, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    idade_resp = models.IntegerField(max_length=3, blank=True, null=True)
    profissao = models.CharField(max_length=70, blank=True, null=True)
    parentesco = models.CharField(max_length=20, blank=True, null=True)
    indicado = models.BooleanField(default=False)
    indicacao = models.CharField(max_length=100, blank=True, null=True)
    faixa_etaria = models.BooleanField(default=False)
    especialidade = models.CharField(max_length=100)
    disponibilidade = models.CharField(max_length=100)
    horario = models.CharField(max_length=5)
    renda = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome

class Consultas(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    data_consulta = models.DateField()
    hora_consulta = models.TimeField()
    especialidade = models.CharField(max_length=100)
    profissional = models.CharField(max_length=100)
    obs = models.TextField()

    def __str__(self):
        return f"Consulta de {self.paciente.nome} em {self.data_consulta}"

class Relatorios(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    data_relatorio = models.DateField()
    queixa = models.TextField()
    diagnostico = models.TextField()
    conduta = models.TextField()

    def __str__(self):
        return f"Relatório de {self.paciente.nome} em {self.data_relatorio}"