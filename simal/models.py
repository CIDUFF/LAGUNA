from datetime import datetime, date, timedelta
import re
import unicodedata
from localflavor.br.models import BRCPFField
from django.db import models
from django.contrib.auth.models import User  # Importa o modelo User



class equipes(models.Model):
    """
    Classe que representa as equipes que usam o sistema.

    Atributos:
        nome (str): O nome da equipe.
        descricao (str): A descrição da equipe.
    """

    nome = models.CharField(max_length=50)
    descricao = models.TextField(max_length=100)
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nome}'

# class UsuarioSistema(models.Model):
#     """
#     Representa um coletor de dados.

#     Atributos:
#         nome (str): O nome do coletor.
#         email (str): O email do coletor.
#         telefone (str): O telefone do coletor.
#         filiacao (str): A filiação do coletor.
#         equipe (str): A equipe do coletor.
#     """

#     nome = models.ForeignKey(User, on_delete=models.CASCADE)


#     def __str__(self):
#         return f'{self.nome}'



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


class Analises(models.Model):
    laboratorio = models.ForeignKey(
        Laboratorios, on_delete=models.CASCADE, related_name='analises')
    analise = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Análise Laboratorial {self.analise}"


class Solicitantes(models.Model):
    """
    Classe que representa os solicitantes.

    Atributos:
        nome (str): O nome do solicitante.
        email (str): O email do solicitante.
        telefone (str): O telefone do solicitante.
    """

    nome = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)

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
    

class Locais(models.Model):
    nome = models.CharField(max_length=50)
    desc = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'tab_local'


    def __str__(self):
        return f'{self.codigo}'

class PontosColeta(models.Model):
    
    DESCRICAO = [
        ('Ponto de Coleta', 'Ponto de Coleta'),
        ('Ponto de aplicação', 'Ponto de Aplicação'),
    ]
    
    nome = models.CharField(max_length=5, blank=False)
    setor = models.ForeignKey('Setor', on_delete=models.CASCADE, related_name='pontos')
    local = models.ForeignKey(Locais, on_delete=models.CASCADE, related_name='pontos')
    tipo = models.CharField(max_length=50, choices=DESCRICAO, default='Ponto de Coleta')
    status = models.BooleanField(default=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.codigo}'

    class Meta:
        db_table = 'tab_ponto'
        

    
    
class Setor(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    local = models.ForeignKey(Locais, on_delete=models.CASCADE, related_name='setor')
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    abreviatura = models.CharField(max_length=50, blank=True, unique=True)

    
    def __str__(self):
        return f'{self.desc}'
    
    class Meta:
        db_table = 'tab_setor'


class ProgramaColeta(models.Model):

    ordem_servico = models.CharField(
        max_length=100, blank=True, verbose_name='Ordem de Serviço')
    data_coleta_campo = models.DateField(
        null=True, verbose_name='Data da Coleta')
    data_programacao = models.DateField(
        auto_now_add=True, null=True, verbose_name='Data da Programação')
    data_check_forecast = models.DateField(
        null=True, verbose_name='Data do Check Forecast')
    data_check_lab = models.DateField(
        null=True, verbose_name='Data do Check Lab')
    data_check_car = models.DateField(
        null=True, verbose_name='Data do Check Car')
    data_check_material = models.DateField(
        null=True, verbose_name='Data do Check Material')
    equipe_coleta = models.CharField(
        max_length=50, default='Equipe 1', verbose_name='Equipe de Coleta')
    # solicitante = models.CharField(
    #     max_length=50, default='João Silva', verbose_name='Responsável')
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
            localizacao = Setor.objects.filter(
                desc=self.local_coleta).first()

            if localizacao:
                codigo = localizacao.abreviatura
                ordem_servico_raw = f"{codigo}{self.data_coleta_campo}{hora}"
                ordem_servico_normalized = unicodedata.normalize(
                    'NFKD', ordem_servico_raw)
                ordem_servico_ascii = ordem_servico_normalized.encode(
                    'ASCII', 'ignore').decode('ASCII')
                self.ordem_servico = re.sub(
                    r'[\s\W_]+', '', ordem_servico_ascii)
            else:
                raise ValueError("Localização não encontrada")

        if usuario:  # Atribui o usuário recebido ao campo usuario
            self.usuario = usuario

        self.data_check_forecast = self.data_coleta_campo - timedelta(days=10)
        self.data_check_material = self.data_coleta_campo - timedelta(days=3)
        self.data_check_car = self.data_coleta_campo - timedelta(days=5)
        self.data_check_lab = self.data_coleta_campo - timedelta(days=7)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.ordem_servico}'


class Campo(models.Model):
    # Supondo que ProgramaColeta e date já foram importados corretamente
    ordem_servico = models.ForeignKey(
        ProgramaColeta, on_delete=models.CASCADE, related_name='ordem_servico_campo')
    codigo_coleta = models.CharField("Código da Coleta", max_length=50, null=True)
    ordem = models.FloatField("Ordem", null=True)
    clima = models.CharField("Clima", max_length=150, null=True)
    data = models.DateField(default=date.today)
    data_coleta = models.DateField("Data da Coleta", null=True)
    hora_inicio = models.TimeField("Hora de Início", blank=True, null=True)
    hora_fim = models.TimeField("Hora de Término", blank=True, null=True)
    ponto = models.CharField("Ponto de Coleta", default="0")
    temperatura = models.FloatField("Temperatura", null=True)
    ph = models.FloatField("pH", null=True)
    orp = models.FloatField("ORP mV", null=True)
    condutividade = models.FloatField("Condutividade uS/cm", null=True)
    turbidez = models.FloatField("Turbidez NTU", null=True)
    od = models.FloatField("OD mg/L", null=True)
    tds = models.FloatField("TDS", null=True)
    salinidade = models.FloatField("Salinidade", null=True)
    status_form = models.CharField(
        "Status", max_length=20, default='Não preenchido')
    check_amostras = models.BooleanField("Check Amostras", default=False)
    observacoes = models.TextField("Observações", max_length=500, blank=True)
    foto = models.ImageField(
        upload_to='fotos_coleta/', null=True, verbose_name='Foto')

    def save(self, *args, **kwargs):
        campos = [
            self.clima, self.data, self.hora_inicio, self.hora_fim, self.ponto,
            self.temperatura, self.ph, self.orp, self.condutividade, self.turbidez,
            self.od, self.tds, self.salinidade
        ]
        if all(campo is not None for campo in campos):
            self.status_form = 'Preenchido'
        else:
            self.status_form = 'Não preenchido'
        super().save(*args, **kwargs)

class MetadadosCampo(models.Model):
    ACESSOS = [
        'Ponte',
        'Caiaque',
        'Margem',
    ]
    AVALIACAO = [
        (-1, 'Negativo'),
        (0, 'Neutro'),
        (1, 'Positivo'),
    ]
    
        
    codigo_coleta = models.ForeignKey(
        Campo, on_delete=models.CASCADE, related_name='metadados_campo')
    acesso_ponto= models.CharField(
        max_length=50, choices=[(acesso, acesso) for acesso in ACESSOS], null=True)
    dragagem = models.IntegerField(
        "Dragagem", choices=AVALIACAO, null=True)
    gigoga = models.IntegerField(
        "Quantidade de gigoga", choices=AVALIACAO, null=True)
    odor = models.IntegerField(
        "Odor", choices=AVALIACAO, null=True)
    fezes = models.IntegerField(
        "Fezes", choices=AVALIACAO, null=True)
    oleo = models.IntegerField(
        "Óleo", choices=AVALIACAO, null=True)
    residuos_solidos = models.IntegerField(
        "Resíduos Sólidos", choices=AVALIACAO, null=True)
    lodo = models.IntegerField(
        "Lodo", choices=AVALIACAO, null=True)
    animais_presentes = models.IntegerField(
        "Animais Presentes", choices=AVALIACAO, null=True)
    pescadores = models.IntegerField(
        "Pescadores", choices=AVALIACAO, null=True)
    contato_populacao = models.IntegerField(
        "Contato com a população", choices=AVALIACAO, null=True)
    
    def __str__(self):
        return f"Metadados do campo {self.codigo_coleta}"
        
        
        
    


class AnalisesLista(models.Model):
    ordem_servico = models.ForeignKey(
        ProgramaColeta, on_delete=models.CASCADE, related_name='analises_lista')
    codigo_coleta = models.ForeignKey(
        Campo, on_delete=models.CASCADE, related_name='analises_lista')
    clorofila = models.FloatField(null=True, blank=True)
    # Material Particulado em Suspensão
    mps = models.FloatField(null=True, blank=True)
    amonia = models.FloatField(null=True, blank=True)  # Amônia
    nitrito = models.FloatField(null=True, blank=True)
    nitrato = models.FloatField(null=True, blank=True)
    nitrogenio_total = models.FloatField(
        null=True, blank=True)  # Nitrogênio Total
    # Ortofosfato como P (Fósforo Reativo Solúvel)
    ortofosfato_como_p = models.FloatField(null=True, blank=True)
    fosfato_total = models.FloatField(null=True, blank=True)
    fosforo_total = models.FloatField(null=True, blank=True)  # Fósforo Total
    # Demanda Bioquímica de Oxigênio
    dbo = models.FloatField(null=True, blank=True)
    materia_organica = models.FloatField(null=True, blank=True)
    cot = models.FloatField(null=True, blank=True)  # Carbono Orgânico Total
    arsenio = models.FloatField(null=True, blank=True)
    cadmio = models.FloatField(null=True, blank=True)
    chumbo = models.FloatField(null=True, blank=True)
    cobre = models.FloatField(null=True, blank=True)
    cromo = models.FloatField(null=True, blank=True)
    mercurio = models.FloatField(null=True, blank=True)
    niquel = models.FloatField(null=True, blank=True)
    zinco = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Análises Lista {self.ordem_servico}"



class ChecklistCampo(models.Model):
    data_checklist = models.DateField(auto_now=True)
    data_limite = models.DateField(auto_now=False, null=True, blank=True)
    ordem_servico = models.ForeignKey(
        'ProgramaColeta', on_delete=models.CASCADE, related_name='checklist_ordem_servico')
    previsao_tempo = models.BooleanField(
        "Previsão do tempo", blank=True, null=True, default=False)
    data_previsao_tempo = models.DateField(
        "Data da previsão", blank=True, null=True)
    observacao_previsao_tempo = models.TextField(
        "Observações da previsão", blank=True, null=True)
    avisar_labs = models.BooleanField(
        "Avisar laboratórios", blank=True, null=True, default=False)
    data_avisar_labs = models.DateField(
        "Data do aviso", blank=True, null=True)
    observacao_avisar_labs = models.TextField(
        "Observações do aviso", blank=True, null=True)
    reservar_carro = models.BooleanField(
        "Reservar carro", blank=True, null=True, default=False)
    observacao_reservar_carro = models.TextField(
        "Observações da reserva", blank=True, null=True)
    data_reservar_carro = models.DateField(
        "Data da reserva", blank=True, null=True)
    reservar_barco = models.BooleanField(
        "Reservar barco", blank=True, null=True, default=False)
    observacao_reservar_barco = models.TextField(
        "Observações da reserva", blank=True, null=True)
    data_reservar_barco = models.DateField(
        "Data da reserva", blank=True, null=True)
    separar_equipamentos = models.BooleanField(
        "Separar equipamentos", blank=True, null=True, default=False)
    data_separar_equipamentos = models.DateField(
        "Data da separação", blank=True, null=True)
    observacao_separar_equipamentos = models.TextField(
        "Observações da separação", blank=True, null=True)
    conferir_equipamentos = models.BooleanField(
        "Conferir equipamentos", blank=True, null=True, default=False)
    data_conferir_equipamentos = models.DateField(
        "Data da conferência", blank=True, null=True)
    observacao_conferir_equipamentos = models.TextField(
        "Observações da conferência", blank=True, null=True)
    comprar_gelo = models.BooleanField(
        "Comprar gelo", blank=True, null=True, default=False)
    data_comprar_gelo = models.DateField(
        "Data da compra", blank=True, null=True)
    observacao_comprar_gelo = models.TextField(
        "Observações da compra", blank=True, null=True)
    etiquetar_frascos = models.BooleanField(
        "Estiquetar frascos", blank=True, null=True, default=False)
    data_etiquetar_frascos = models.DateField(
        "Data da etiquetagem", blank=True, null=True)
    observacao_etiquetar_frascos = models.TextField(
        "Observações da etiquetagem", blank=True, null=True)
        
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
        """Sobrescreve o método save para atualizar o status e o progresso antes de salvar e registrar logs de alterações."""
        user = kwargs.pop('usuario', None)
        if self.pk:
            # Obter o estado atual do objeto do banco de dados
            old_instance = ChecklistCampo.objects.get(pk=self.pk)
            # Verificar alterações e registrar logs
            for field in self._meta.fields:
                field_name = field.name
                # Ignorar campos que não queremos logar
                if field_name not in ['id', 'data_checklist']:
                    old_value = getattr(old_instance, field_name)
                    new_value = getattr(self, field_name)
                    if old_value != new_value:
                        ChecklistCampoLog.objects.create(
                            checklist=self,
                            campo_alterado=field_name,
                            valor_antigo=str(old_value),
                            valor_novo=str(new_value),
                            usuario=user
                        )

        self.status_checklist = all(self.campos_booleanos)
        self.progresso = self.percentual_conclusao
        super().save(*args, **kwargs)


class ChecklistCampoLog(models.Model):
    checklist = models.ForeignKey(
        ChecklistCampo, on_delete=models.CASCADE, related_name='logs')
    data_alteracao = models.DateTimeField(auto_now=True)
    campo_alterado = models.CharField(max_length=100)
    valor_antigo = models.TextField(null=True, blank=True)
    valor_novo = models.TextField(null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Log de {self.checklist} em {self.data_alteracao} por {self.usuario}'
    

class DetalhesUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15, blank=True)
    endereco = models.CharField(max_length=100, blank=True)
    cpf = BRCPFField(blank=True)


    def __str__(self):
        return f'{self.usuario}'
