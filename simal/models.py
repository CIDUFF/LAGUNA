from datetime import datetime, date
import random
import string
from django.db import models


class Coletores(models.Model):
    nome = models.CharField(max_length=100, default= 'Nome do Coletor')
    email = models.EmailField(max_length=100, default = 'seuemail@email.com')
    telefone = models.CharField(max_length=15, default='(21) 99999-9999')
    filiacao = models.CharField(max_length=100, default='UFF')
    equipe = models.CharField(max_length=25, default='Equipe 1')

    def __str__(self):
        return f'{self.nome}'

class Laboratorios(models.Model):
    TIPO_CHOICES = [
        ('interno', 'Interno'),
        ('externo', 'Externo'),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefone = models.CharField(max_length=15)
    endereco = models.CharField(max_length=100)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    
    def __str__(self):
        return f'{self.nome}'

class Solicitantes(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.nome}'

class LocaisColeta(models.Model):
    local = models.CharField(max_length=50)
    local_codigo = models.CharField(max_length=50,default='00') # Código numérico começando em 01 para cada local no DB
    ponto = models.CharField(max_length=60, blank=False)
    codigo = models.CharField(max_length=60, blank=False)
    # rota = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f'{self.local}'

class ProgramaColeta(models.Model):
    
    STATUS = [
        ('programada', 'Programada'),
        ('reprogramada', 'Reprogramada'), 
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    ordem_servico = models.CharField(max_length=20, blank=True)
    data_coleta_campo = models.DateField(auto_now=False, auto_now_add=False)
    equipe_coleta = models.ForeignKey(Coletores, on_delete=models.CASCADE, related_name='programa_coletor')
    laboratorio = models.ForeignKey(Laboratorios, on_delete=models.CASCADE, related_name='programa_laboratorio')
    solicitante = models.ForeignKey(Solicitantes, on_delete=models.CASCADE, related_name='programa_solicitante')
    ponto_coleta = models.ForeignKey(LocaisColeta, on_delete=models.CASCADE, related_name='programa_ponto_coleta')
    status_coleta = models.CharField(max_length=12, choices=STATUS, default='programada')
    observacoes = models.TextField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        if not self.ordem_servico:
            data = datetime.now().strftime('%Y%m%d')  # Data atual no formato AAAAMMDD
            numero_aleatorio = ''.join(random.choices(string.digits, k=5))  # Número aleatório de 5 dígitos
            primeira_palavra_local = self.ponto_coleta.ponto.split(' ')[0]  # Primeira palavra do local
            self.ordem_servico = f'{data}-{numero_aleatorio}-{primeira_palavra_local}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Coleta da água em {self.ponto_coleta} em {self.data_coleta_campo}'
    
class Campo(models.Model):
    
    CLIMA_CHOICES = [
        ('sol', 'Sol'),
        ('chuva', 'Chuva'),
        ('nublado', 'Nublado'),
        ('vento', 'Vento'),
    ]
    
    MATRIZ = [
        ('agua_marinha', 'Água marinha'),
        ('agua_doce', 'Água doce'),
        ('agua_salobra', 'Água salobra'),
        ('agua_salina', 'Água salina'),
    ]
    
    clima = models.CharField("Clima", max_length=7, choices=CLIMA_CHOICES)
    matriz = models.CharField("Matriz", max_length=12, choices=MATRIZ)
    hora_inicio = models.TimeField("Hora de Início", auto_now=False, auto_now_add=False)
    hora_fim = models.TimeField("Hora de Término", auto_now=False, auto_now_add=False)
    data = models.DateField(default=date.today)
    tempo = models.DurationField("Duração", editable=False)
    ponto = models.IntegerField("Ponto de Coleta", null=True)
    temperatura = models.DecimalField("Temperatura", max_digits=5, decimal_places=2)
    ph = models.DecimalField("pH", max_digits=5, decimal_places=2)
    orp = models.IntegerField("ORP mV")
    condutividade = models.DecimalField("Condutividade uS/cm", max_digits=5, decimal_places=2)
    turbidez = models.DecimalField("Turbidez NTU", max_digits=5, decimal_places=2)
    od = models.DecimalField("OD mg/L", max_digits=5, decimal_places=2)
    od_pct = models.DecimalField("OD %", max_digits=5, decimal_places=2)
    tds = models.DecimalField("TDS", max_digits=5, decimal_places=2)
    salinidade = models.DecimalField("Salinidade", max_digits=5, decimal_places=2)


    def save(self, *args, **kwargs):
            datetime_inicio = datetime.combine(date.today(), self.hora_inicio)
            datetime_fim = datetime.combine(date.today(), self.hora_fim)
            self.tempo = datetime_fim - datetime_inicio
            super().save(*args, **kwargs)
            
class ListaColeta(models.Model):
    STATUS = [
        ('programada', 'Programada'),
        ('reprogramada', 'Reprogramada'), 
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    data_coleta_campo = models.DateField(auto_now=False, auto_now_add=False)
    equipe_coleta = models.ForeignKey(Coletores, on_delete=models.CASCADE, related_name='lista_coletor')
    laboratorio = models.ForeignKey(Laboratorios, on_delete=models.CASCADE, related_name='lista_laboratorio')
    solicitante = models.ForeignKey(Solicitantes, on_delete=models.CASCADE, related_name='lista_solicitante')
    ponto_coleta = models.ForeignKey(LocaisColeta, on_delete=models.CASCADE, related_name='lista_ponto_coleta')
    status_coleta = models.CharField(max_length=12, choices=STATUS, default='programada')
    observacoes = models.TextField(max_length=500, blank=True)
    campo = models.OneToOneField(Campo, on_delete=models.CASCADE, related_name='campo')

    def __str__(self):
        return f'Coleta da água em {self.ponto_coleta} em {self.data_coleta_campo}'