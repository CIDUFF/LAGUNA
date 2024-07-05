from datetime import datetime, date
from django.db import models
from django.utils.crypto import get_random_string
import re
import unicodedata
# import random
# import string


class Coletores(models.Model):
    nome = models.CharField(max_length=100, default= 'Nome do Coletor')
    email = models.EmailField(max_length=100, default = 'seuemail@email.com')
    telefone = models.CharField(max_length=15, default='(21) 99999-9999')
    filiacao = models.CharField(max_length=100, default='UFF')
    equipe = models.CharField(max_length=25, default='Equipe 1')

    def __str__(self):
        return f'{self.nome}'

class Ajuda(models.Model):
    nome = models.CharField(max_length=15)
    email = models.EmailField(max_length=100, default = 'seuemail@email.com')
    pergunta = models.TextField(max_length=250)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return f'{self.nome}'

class Laboratorios(models.Model):

    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefone = models.CharField(max_length=100)
    endereco = models.CharField(max_length=100)
    tipo = models.CharField(max_length=25)
    
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
    ANALISE = [
        ('Água', 'Sedimentos')
    ]

    ordem_servico = models.CharField(max_length=200, blank=True)
    data_coleta_campo = models.DateField(null=True)
    data_fim_coleta_campo = models.DateField(null= True)
    equipe_coleta = models.CharField(max_length=50, default='Equipe 1')
    laboratorio = models.CharField(max_length=50,default='Interno')
    solicitante = models.CharField(max_length=50, default='João Silva')
    local_coleta = models.CharField(max_length=50)
    tipos_analise = models.CharField(max_length=50, choices=ANALISE, default='Água')
    status_coleta = models.CharField(max_length=12, choices=STATUS, default='programada')
    observacoes = models.TextField(max_length=500, blank=True)
    
    # checklist = models.CharField(max_length=1, choices=[(0, 'Não realizada'), (1, 'Realizada')])
    
    
    def save(self, *args, **kwargs):
        if not self.ordem_servico:
            
            # Gera uma ordem de serviço única combinando código do local, data formatada e string aleatória
            ordem_servico_raw = f"{self.local_coleta}{self.data_coleta_campo}{get_random_string(length=4)}"

            # Normaliza, remove acentos, converte para minúsculas e remove caracteres especiais
            ordem_servico_normalized = unicodedata.normalize(
                'NFKD', ordem_servico_raw)
            ordem_servico_ascii = ordem_servico_normalized.encode(
                'ASCII', 'ignore').decode('ASCII')
            ordem_servico_clean = re.sub(
                r'[\s\W_]+', '', ordem_servico_ascii).lower()

            self.ordem_servico = ordem_servico_clean

        super().save(*args, **kwargs)



    def __str__(self):
        return f'{self.local_coleta} em {self.data_coleta_campo}, OS: {self.ordem_servico}'
    
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
    
    ordem_servico = models.ForeignKey(ProgramaColeta, on_delete=models.CASCADE, related_name='ordem_servico_campo')
    codigo_coleta = models.CharField("Código da Coleta", max_length=50, blank=True)
    clima = models.CharField("Clima", max_length=7, choices=CLIMA_CHOICES)
    matriz = models.CharField("Matriz", max_length=12, choices=MATRIZ)
    hora_inicio = models.TimeField("Hora de Início", auto_now=False, auto_now_add=False)
    hora_fim = models.TimeField("Hora de Término", auto_now=False, auto_now_add=False)
    data = models.DateField(default=date.today)
    # tempo = models.DurationField("Duração", editable=False)
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
    
class ChecklistCampo(models.Model):
    
    STATUS = [
        ('concluido', 'Concluído'),
        ('pendente', 'Pendente'),
    ]
    data_checklist = models.DateField(auto_now=True)
    ordem_servico = models.ForeignKey(ProgramaColeta, on_delete=models.CASCADE, related_name='checklist_ordem_servico')
    previsao_tempo = models.BooleanField("Previsão do tempo", blank=True, null=True)
    avisar_labs = models.BooleanField("Avisar laboratórios", blank=True, null=True)
    reservar_carro = models.BooleanField("Reservar carro", blank=True, null=True)
    reservar_barco = models.BooleanField("Reservar barco", blank=True, null=True)
    separar_equipamentos = models.BooleanField("Separar equipamentos", blank=True, null=True)
    conferir_equipamentos = models.BooleanField("Conferir equipamentos", blank=True, null=True)
    comprar_gelo = models.BooleanField("Comprar gelo", blank=True, null=True)
    observacoes = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return f'Checklist da coleta em {self.data_checklist}'