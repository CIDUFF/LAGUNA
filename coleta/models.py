from django.db import models

class Coleta_lagoa(models.Model):
    pH = models.DecimalField(max_digits=4, decimal_places=2)
    temperatura = models.DecimalField(max_digits=4, decimal_places=2)
    turbidez = models.DecimalField(max_digits=4, decimal_places=2)
    oxigenio_dissolvido = models.DecimalField(max_digits=4, decimal_places=2)
    data_coleta = models.DateField(auto_now=False, auto_now_add=False)
    local_coleta = models.CharField(max_length=100)
    responsavel_coleta = models.CharField(max_length=100) #adicionar um model para cadastro de coletores
    observacoes = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return f'Coleta da água em {self.local_coleta} em {self.data_coleta}'
    