from datetime import datetime, date
from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import re
import unicodedata
from django.contrib.auth.models import User  # Importa o modelo User
# import random
# import string


class Coletores(models.Model):
    """
    Representa um coletor de dados.

    Atributos:
        nome (str): O nome do coletor.
        email (str): O email do coletor.
        telefone (str): O telefone do coletor.
        filiacao (str): A filiação do coletor.
        equipe (str): A equipe do coletor.
    """

    nome = models.CharField(max_length=100, default='Nome do Coletor')
    email = models.EmailField(max_length=100, default='seuemail@email.com')
    telefone = models.CharField(max_length=15, default='(21) 99999-9999')
    filiacao = models.CharField(max_length=100, default='UFF')
    equipe = models.CharField(max_length=25, default='Equipe 1')

    def __str__(self):
        return f'{self.nome}'


class Ajuda(models.Model):
    """
    Classe que representa uma solicitação de ajuda.

    Atributos:
        nome (str): O nome do solicitante.
        email (str): O endereço de e-mail do solicitante.
        pergunta (str): A pergunta ou descrição da solicitação de ajuda.
        data (datetime): A data e hora em que a solicitação foi feita.
    """

    nome = models.CharField(max_length=15)
    email = models.EmailField(max_length=100, default='seuemail@email.com')
    pergunta = models.TextField(max_length=250)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome}'


class Laboratorios(models.Model):
    """
    Classe que representa um laboratório.

    Atributos:
        nome (str): O nome do laboratório.
        email (str): O email do laboratório.
        telefone (str): O telefone do laboratório.
        endereco (str): O endereço do laboratório.
        tipo (str): O tipo de laboratório.

    Métodos:
        __str__(): Retorna uma representação em string do objeto Laboratorios.
    """

    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefone = models.CharField(max_length=100)
    endereco = models.CharField(max_length=100)
    tipo = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.nome}'


class Solicitantes(models.Model):
    """
    Classe que representa os solicitantes.

    Atributos:
        nome (str): O nome do solicitante.
        email (str): O email do solicitante.
        telefone (str): O telefone do solicitante.
    """

    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.nome}'


class LocaisColeta(models.Model):
    """
    Classe que representa os locais de coleta no banco de dados.

    Atributos:
        local (str): O nome do local de coleta.
        local_codigo (str): O código numérico do local de coleta.
        ponto (str): O ponto de coleta.
        codigo_str (str): O código em formato de string.
    """

    local = models.CharField(max_length=50)
    local_codigo = models.CharField(max_length=50, default='00')
    ponto = models.CharField(max_length=60, blank=False)
    codigo_str = models.CharField(max_length=60, blank=False)
    # rota = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.local}'


class ProgramaColeta(models.Model):

    ordem_servico = models.CharField(
        max_length=100, blank=True, verbose_name='Ordem de Serviço')
    data_coleta_campo = models.DateField(
        null=True, verbose_name='Data da Coleta')
    equipe_coleta = models.CharField(
        max_length=50, default='Equipe 1', verbose_name='Equipe de Coleta')
    solicitante = models.CharField(
        max_length=50, default='João Silva', verbose_name='Responsável')
    local_coleta = models.CharField(
        max_length=50, verbose_name='Local de Coleta')
    status_coleta = models.CharField(max_length=50, null=True)
    observacoes = models.TextField(
        max_length=500, blank=True, verbose_name='Observações')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,
                                verbose_name="Usuário", null=True)  # Adiciona o campo usuario
    rota = models.CharField(max_length=25, null=True)

    def save(self, usuario=None, *args, **kwargs):

        if not self.ordem_servico:
            hora = datetime.now().strftime('%H%M%S')
            localizacao = LocaisColeta.objects.filter(local=self.local_coleta).first()

            if localizacao:
                codigo = localizacao.codigo_str
                ordem_servico_raw = f"{codigo}{self.data_coleta_campo}{hora}"
                ordem_servico_normalized = unicodedata.normalize(
                    'NFKD', ordem_servico_raw)
                ordem_servico_ascii = ordem_servico_normalized.encode(
                    'ASCII', 'ignore').decode('ASCII')
                self.ordem_servico = re.sub(r'[\s\W_]+', '', ordem_servico_ascii)
            else:
                raise ValueError("Localização não encontrada")

        if usuario:  # Atribui o usuário recebido ao campo usuario
            self.usuario = usuario

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.ordem_servico}'


class Campo(models.Model):
    # Supondo que ProgramaColeta e date já foram importados corretamente
    ordem_servico = models.ForeignKey(
        ProgramaColeta, on_delete=models.CASCADE, related_name='ordem_servico_campo')
    codigo_coleta = models.CharField("Código da Coleta", max_length=50)
    ordem = models.FloatField("Ordem", null=True)
    clima = models.CharField("Clima", max_length=150, null=True)
    data = models.DateField(default=date.today)
    hora_inicio = models.TimeField("Hora de Início", blank=True, null=True)
    hora_fim = models.TimeField("Hora de Término", blank=True, null=True)
    ponto = models.CharField("Ponto de Coleta", default="0")
    temperatura = models.FloatField("Temperatura", null=True)
    ph = models.FloatField("pH", null=True)
    orp = models.FloatField("ORP mV", null=True)
    condutividade = models.FloatField("Condutividade uS/cm", null=True)
    turbidez = models.FloatField("Turbidez NTU", null=True)
    od = models.FloatField("OD mg/L", null=True)
    od_pct = models.FloatField("OD %", null=True)
    tds = models.FloatField("TDS", null=True)
    salinidade = models.FloatField("Salinidade", null=True)
    status_form = models.CharField(
        "Status", max_length=20, default='Não preenchido')

    def save(self, *args, **kwargs):
        campos = [
            self.clima, self.data, self.hora_inicio, self.hora_fim, self.ponto,
            self.temperatura, self.ph, self.orp, self.condutividade, self.turbidez,
            self.od, self.od_pct, self.tds, self.salinidade
        ]
        if all(campo is not None for campo in campos):
            self.status_form = 'Preenchido'
        super().save(*args, **kwargs)


class ListaColeta(models.Model):
    STATUS = [
        ('programada', 'Programada'),
        ('reprogramada', 'Reprogramada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    data_coleta_campo = models.DateField(auto_now=False, auto_now_add=False)
    equipe_coleta = models.ForeignKey(
        Coletores, on_delete=models.CASCADE, related_name='lista_coletor')
    laboratorio = models.ForeignKey(
        Laboratorios, on_delete=models.CASCADE, related_name='lista_laboratorio')
    solicitante = models.ForeignKey(
        Solicitantes, on_delete=models.CASCADE, related_name='lista_solicitante')
    ponto_coleta = models.ForeignKey(
        LocaisColeta, on_delete=models.CASCADE, related_name='lista_ponto_coleta')
    status_coleta = models.CharField(
        max_length=12, choices=STATUS, default='programada')
    observacoes = models.TextField(max_length=500, blank=True)
    campo = models.OneToOneField(
        Campo, on_delete=models.CASCADE, related_name='campo')

    def __str__(self):
        return f'Coleta da água em {self.ponto_coleta} em {self.data_coleta_campo}'


class ChecklistCampo(models.Model):
    data_checklist = models.DateField(auto_now=True)
    ordem_servico = models.ForeignKey(
        'ProgramaColeta', on_delete=models.CASCADE, related_name='checklist_ordem_servico')
    previsao_tempo = models.BooleanField(
        "Previsão do tempo", blank=True, null=True)
    avisar_labs = models.BooleanField(
        "Avisar laboratórios", blank=True, null=True)
    reservar_carro = models.BooleanField(
        "Reservar carro", blank=True, null=True)
    reservar_barco = models.BooleanField(
        "Reservar barco", blank=True, null=True)
    separar_equipamentos = models.BooleanField(
        "Separar equipamentos", blank=True, null=True)
    conferir_equipamentos = models.BooleanField(
        "Conferir equipamentos", blank=True, null=True)
    comprar_gelo = models.BooleanField("Comprar gelo", blank=True, null=True)
    observacoes = models.TextField(max_length=500, blank=True)
    status_checklist = models.BooleanField(default=False)
    progresso = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        """Representação em string do ChecklistCampo."""
        return f'Checklist da coleta em {self.data_checklist}'

    @property
    def campos_booleanos(self):
        """Retorna uma lista de todos os campos booleanos."""
        return [
            self.previsao_tempo, self.avisar_labs, self.reservar_carro,
            self.reservar_barco, self.separar_equipamentos,
            self.conferir_equipamentos, self.comprar_gelo
        ]

    @property
    def percentual_conclusao(self):
        """Calcula o percentual de conclusão do checklist."""
        campos_marcados = sum(bool(campo) for campo in self.campos_booleanos)
        total_campos = len(self.campos_booleanos)
        return (campos_marcados / total_campos) * 100 if total_campos > 0 else 0

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para atualizar o status e o progresso antes de salvar."""
        self.status_checklist = all(self.campos_booleanos)
        self.progresso = self.percentual_conclusao
        super().save(*args, **kwargs)
