from django.db import models

class Coletores(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefone = models.CharField(max_length=15)
    filiacao = models.CharField(max_length=100)

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
    ponto_coleta = models.IntegerField(default=0)
    codigo = models.CharField(max_length=60, blank=True)
    rota = models.CharField(max_length=100, blank=True)
    
    def save(self, *args, **kwargs):
        codigo_local = ''.join(palavra[0] for palavra in self.local.split())
        self.codigo = f'{codigo_local}{self.ponto_coleta}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.local}'

class ProgramaColeta(models.Model):
    
    STATUS = [
        ('programada', 'Programada'),
        ('reprogramada', 'Reprogramada'), 
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    data_coleta_campo = models.DateField(auto_now=False, auto_now_add=False)
    equipe_coleta = models.ForeignKey(Coletores, on_delete=models.CASCADE, related_name='coletor')
    laboratorio = models.ForeignKey(Laboratorios, on_delete=models.CASCADE, related_name='laboratorio')
    solicitante = models.ForeignKey(Solicitantes, on_delete=models.CASCADE, related_name='solicitante')
    ponto_coleta = models.ForeignKey(LocaisColeta, on_delete=models.CASCADE, related_name='ponto_coleta')
    status_coleta = models.CharField(max_length=12, choices=STATUS, default='programada')
    observacoes = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'Coleta da água em {self.ponto_coleta.local} em {self.data_coleta_campo}'
    

class ColetaDeCampo(models.Model):
    
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
    data = models.ForeignKey(ProgramaColeta, on_delete=models.CASCADE, related_name='data')
    tempo = models.DurationField("Duração", editable=False)
    ponto = models.ForeignKey(LocaisColeta, on_delete=models.CASCADE, related_name='ponto')
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
        self.tempo = self.hora_fim - self.hora_inicio
        super().save(*args, **kwargs)
    

