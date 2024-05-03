from django.db import models

class Coleta_lagoa(models.Model):
    """
    Represents a water collection from a lagoon.

    Attributes:
        pH (DecimalField): The pH value of the water sample.
        temperatura (DecimalField): The temperature of the water sample.
        turbidez (DecimalField): The turbidity of the water sample.
        oxigenio_dissolvido (DecimalField): The dissolved oxygen of the water sample.
        data_coleta (DateField): The date of the water collection.
        local_coleta (CharField): The location of the water collection.
        responsavel_coleta (CharField): The person responsible for the water collection.
        observacoes (TextField): Additional observations about the water sample.
    """

    # pH = models.DecimalField(max_digits=4, decimal_places=2)
    # temperatura = models.IntegerField(("Temperatura da água"), default=0)
    # turbidez = models.DecimalField(max_digits=4, decimal_places=2)
    # oxigenio_dissolvido = models.DecimalField(max_digits=4, decimal_places=2)
    # data_coleta = models.DateField(auto_now=False, auto_now_add=False)
    # local_coleta = models.CharField(max_length=100)
    # responsavel_coleta = models.CharField(max_length=100) #adicionar um model para cadastro de coletores
    # observacoes = models.TextField(max_length=500, blank=True)
    
    
    data_coleta_campo = models.DateField(auto_now=False, auto_now_add=False)
    codigo_amostra = models.CharField(max_length=50)
    coletor = models.ForeignKey('coletores', on_delete=models.CASCADE, related_name='coletor')
    laboratorio = models.ForeignKey('Laboratorios', on_delete=models.CASCADE, related_name='laboratorio')
    solicitante = models.ForeignKey('solicitantes', on_delete=models.CASCADE, related_name='solicitante')
    ponto_coleta = models.ForeignKey('locais_coleta', on_delete=models.CASCADE, related_name='ponto_coleta')

    
    def __str__(self):
        return f'Coleta da água em {self.local_coleta} em {self.data_coleta}'
    
class coletores(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefone = models.CharField(max_length=15)
    filiacao = models.CharField(max_length=100)

    
    def __str__(self):
        return f'{self.nome}'
    
class analistas(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefone = models.CharField(max_length=15)
    filiacao = models.CharField(max_length=100)
    organizacao = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.nome}'
    
class locais_coleta(models.Model):
    local = models.CharField(max_length=50)
    ponto_coleta = models.IntegerField(default=0)
    codigo = models.CharField(max_length=60, blank=True)
    
    def save(self, *args, **kwargs):
        codigo_local = ''.join(palavra[0] for palavra in self.local.split())
        self.codigo = f'{codigo_local}{self.ponto_coleta}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.local}'

class tipos_analise(models.Model):
    analise = models.CharField(max_length=50)
    unidade_medida = models.CharField(max_length=10)
    
    def __str__(self):
        return f'{self.analise}'

class solicitantes(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefone = models.CharField(max_length=15)

    
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

