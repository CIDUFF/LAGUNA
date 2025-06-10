from datetime import datetime, date, timedelta
from django.utils import timezone
import re
import unicodedata

# from localflavor.br.models import BRCPFField
from django.db import models
from django.contrib.auth.models import User  # Importa o modelo User
from phonenumber_field.modelfields import PhoneNumberField


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
    email = models.EmailField(max_length=100, default="seuemail@email.com")
    pergunta = models.TextField(max_length=250)
    data = models.DateTimeField(auto_now_add=True)
    anexo = models.FileField(upload_to="media/anexo_ajuda", blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"


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
        return f"{self.nome}"


class Analises(models.Model):
    laboratorio = models.ForeignKey(
        Laboratorios, on_delete=models.CASCADE, related_name="analises"
    )
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
        return f"{self.nome}"


class ProgramaColeta(models.Model):
    ordem_servico = models.CharField(
        max_length=100, blank=True, verbose_name="Ordem de Serviço"
    )
    data_coleta_campo = models.DateField(null=True, verbose_name="Data da Coleta")
    data_programacao = models.DateField(
        auto_now_add=True, null=True, verbose_name="Data da Programação"
    )
    data_check_forecast = models.DateField(
        null=True, verbose_name="Data do Check Forecast"
    )
    data_check_lab = models.DateField(null=True, verbose_name="Data do Check Lab")
    data_check_car = models.DateField(null=True, verbose_name="Data do Check Car")
    data_check_material = models.DateField(
        null=True, verbose_name="Data do Check Material"
    )
    prazo_previsao = models.FloatField(
        null=True, verbose_name="Prazo para previsão do tempo", default=10
    )
    prazo_lab = models.FloatField(
        null=True, verbose_name="Prazo para aviso ao laboratório", default=7
    )
    prazo_car = models.FloatField(
        null=True, verbose_name="Prazo para reserva de carro", default=5
    )
    prazo_material = models.FloatField(
        null=True, verbose_name="Prazo para check de material", default=3
    )
    equipe_coleta = models.CharField(max_length=50, verbose_name="Equipe de Coleta")
    # solicitante = models.CharField(
    #     max_length=50, default='João Silva', verbose_name='Responsável')
    local_coleta = models.CharField(max_length=50, verbose_name="Local de Coleta")
    status_coleta = models.CharField(max_length=50, null=True)
    observacoes = models.TextField(
        max_length=500, blank=True, verbose_name="Observações"
    )
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Usuário", null=True
    )  # Adiciona o campo usuario
    rota = models.CharField(max_length=25, null=True)
    bentos = models.BooleanField(default=False, verbose_name="Bentos", blank=True)

    def save(self, usuario=None, *args, **kwargs):
        if not self.ordem_servico:
            hora = datetime.now().strftime("%H%M%S")
            localizacao = TabSetor.objects.filter(nome=self.local_coleta).first()

            if localizacao:
                codigo = localizacao.abreviatura
                setor_id = localizacao.id
                ordem_servico_raw = f"{codigo}{setor_id}{self.data_coleta_campo}{hora}"
                ordem_servico_normalized = unicodedata.normalize(
                    "NFKD", ordem_servico_raw
                )
                ordem_servico_ascii = ordem_servico_normalized.encode(
                    "ASCII", "ignore"
                ).decode("ASCII")
                self.ordem_servico = re.sub(r"[\s\W_]+", "", ordem_servico_ascii)
            else:
                raise ValueError("Localização não encontrada")

        if usuario:  # Atribui o usuário recebido ao campo usuario
            self.usuario = usuario

        self.data_check_forecast = self.data_coleta_campo - timedelta(
            self.prazo_previsao
        )
        self.data_check_material = self.data_coleta_campo - timedelta(
            self.prazo_material
        )
        self.data_check_car = self.data_coleta_campo - timedelta(self.prazo_car)
        self.data_check_lab = self.data_coleta_campo - timedelta(self.prazo_lab)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ordem_servico}"


class Campo(models.Model):
    # Supondo que ProgramaColeta e date já foram importados corretamente
    ordem_servico = models.ForeignKey(
        ProgramaColeta, on_delete=models.CASCADE, related_name="ordem_servico_campo"
    )
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
    od_pct = models.FloatField("OD %", null=True)
    tds = models.FloatField("TDS", null=True)
    salinidade = models.FloatField("Salinidade", null=True)
    status_form = models.CharField("Status", max_length=20, default="Não preenchido")
    check_amostras = models.BooleanField("Check Amostras", default=False)
    observacoes = models.TextField("Observações", max_length=500, blank=True)
    foto = models.ImageField(upload_to="fotos_coleta/", null=True, verbose_name="Foto")

    def save(self, *args, **kwargs):
        campos = [
            self.clima,
            self.data,
            self.hora_inicio,
            self.hora_fim,
            self.ponto,
            self.temperatura,
            self.ph,
            self.orp,
            self.condutividade,
            self.turbidez,
            self.od,
            self.tds,
            self.salinidade,
        ]
        if all(campo is not None for campo in campos):
            self.status_form = "Preenchido"
        else:
            self.status_form = "Não preenchido"
        super().save(*args, **kwargs)


class MetadadosCampo(models.Model):
    ACESSOS = [
        "Ponte",
        "Caiaque",
        "Margem",
    ]
    AVALIACAO = [
        (-1, "Negativo"),
        (0, "Neutro"),
        (1, "Positivo"),
    ]

    codigo_coleta = models.ForeignKey(
        Campo, on_delete=models.CASCADE, related_name="metadados_campo"
    )
    acesso_ponto = models.CharField(
        max_length=50, choices=[(acesso, acesso) for acesso in ACESSOS], null=True
    )
    dragagem = models.IntegerField("Dragagem", choices=AVALIACAO, null=True)
    gigoga = models.IntegerField("Quantidade de gigoga", choices=AVALIACAO, null=True)
    odor = models.IntegerField("Odor", choices=AVALIACAO, null=True)
    fezes = models.IntegerField("Fezes", choices=AVALIACAO, null=True)
    oleo = models.IntegerField("Óleo", choices=AVALIACAO, null=True)
    residuos_solidos = models.IntegerField(
        "Resíduos Sólidos", choices=AVALIACAO, null=True
    )
    lodo = models.IntegerField("Lodo", choices=AVALIACAO, null=True)
    animais_presentes = models.IntegerField(
        "Animais Presentes", choices=AVALIACAO, null=True
    )
    pescadores = models.IntegerField("Pescadores", choices=AVALIACAO, null=True)
    contato_populacao = models.IntegerField(
        "Contato com a população", choices=AVALIACAO, null=True
    )

    def __str__(self):
        return f"Metadados do campo {self.codigo_coleta}"

    class Meta:
        db_table = "tab_metadados_campo"


class AnalisesLista(models.Model):
    ordem_servico = models.ForeignKey(
        ProgramaColeta, on_delete=models.CASCADE, related_name="analises_lista"
    )
    codigo_coleta = models.ForeignKey(
        Campo, on_delete=models.CASCADE, related_name="analises_lista"
    )
    clorofila = models.FloatField(null=True, blank=True)
    # Material Particulado em Suspensão
    mps = models.FloatField(null=True, blank=True)
    amonia = models.FloatField(null=True, blank=True)  # Amônia
    nitrito = models.FloatField(null=True, blank=True)
    nitrato = models.FloatField(null=True, blank=True)
    nitrogenio_total = models.FloatField(null=True, blank=True)  # Nitrogênio Total
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
        "ProgramaColeta",
        on_delete=models.CASCADE,
        related_name="checklist_ordem_servico",
    )
    previsao_tempo = models.BooleanField(
        "Previsão do tempo", blank=True, null=True, default=False
    )
    data_previsao_tempo = models.DateField("Data da previsão", blank=True, null=True)
    observacao_previsao_tempo = models.TextField(
        "Observações da previsão", blank=True, null=True
    )
    avisar_labs = models.BooleanField(
        "Avisar laboratórios", blank=True, null=True, default=False
    )
    data_avisar_labs = models.DateField("Data do aviso", blank=True, null=True)
    observacao_avisar_labs = models.TextField(
        "Observações do aviso", blank=True, null=True
    )
    reservar_carro = models.BooleanField(
        "Reservar carro", blank=True, null=True, default=False
    )
    observacao_reservar_carro = models.TextField(
        "Observações da reserva", blank=True, null=True
    )
    data_reservar_carro = models.DateField("Data da reserva", blank=True, null=True)
    reservar_barco = models.BooleanField(
        "Reservar barco", blank=True, null=True, default=False
    )
    observacao_reservar_barco = models.TextField(
        "Observações da reserva", blank=True, null=True
    )
    data_reservar_barco = models.DateField("Data da reserva", blank=True, null=True)
    separar_equipamentos = models.BooleanField(
        "Separar equipamentos", blank=True, null=True, default=False
    )
    data_separar_equipamentos = models.DateField(
        "Data da separação", blank=True, null=True
    )
    observacao_separar_equipamentos = models.TextField(
        "Observações da separação", blank=True, null=True
    )
    conferir_equipamentos = models.BooleanField(
        "Conferir equipamentos", blank=True, null=True, default=False
    )
    data_conferir_equipamentos = models.DateField(
        "Data da conferência", blank=True, null=True
    )
    observacao_conferir_equipamentos = models.TextField(
        "Observações da conferência", blank=True, null=True
    )
    comprar_gelo = models.BooleanField(
        "Comprar gelo", blank=True, null=True, default=False
    )
    data_comprar_gelo = models.DateField("Data da compra", blank=True, null=True)
    observacao_comprar_gelo = models.TextField(
        "Observações da compra", blank=True, null=True
    )
    etiquetar_frascos = models.BooleanField(
        "Estiquetar frascos", blank=True, null=True, default=False
    )
    data_etiquetar_frascos = models.DateField(
        "Data da etiquetagem", blank=True, null=True
    )
    observacao_etiquetar_frascos = models.TextField(
        "Observações da etiquetagem", blank=True, null=True
    )

    status_checklist = models.BooleanField(default=False)
    progresso = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        """Representação em string do ChecklistCampo."""
        return f"Checklist da coleta em {self.data_checklist}"

    @property
    def campos_booleanos(self):
        """Retorna uma lista de todos os campos booleanos."""
        return [
            self.previsao_tempo,
            self.avisar_labs,
            self.reservar_carro,
            self.reservar_barco,
            self.separar_equipamentos,
            self.conferir_equipamentos,
            self.comprar_gelo,
        ]

    @property
    def percentual_conclusao(self):
        """Calcula o percentual de conclusão do checklist."""
        campos_marcados = sum(bool(campo) for campo in self.campos_booleanos)
        total_campos = len(self.campos_booleanos)
        return (campos_marcados / total_campos) * 100 if total_campos > 0 else 0

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para atualizar o status e o progresso antes de salvar e registrar logs de alterações."""
        user = kwargs.pop("usuario", None)
        if self.pk:
            # Obter o estado atual do objeto do banco de dados
            old_instance = ChecklistCampo.objects.get(pk=self.pk)
            # Verificar alterações e registrar logs
            for field in self._meta.fields:
                field_name = field.name
                # Ignorar campos que não queremos logar
                if field_name not in ["id", "data_checklist"]:
                    old_value = getattr(old_instance, field_name)
                    new_value = getattr(self, field_name)
                    if old_value != new_value:
                        ChecklistCampoLog.objects.create(
                            checklist=self,
                            campo_alterado=field_name,
                            valor_antigo=str(old_value),
                            valor_novo=str(new_value),
                            usuario=user,
                        )

        self.status_checklist = all(self.campos_booleanos)
        self.progresso = self.percentual_conclusao
        super().save(*args, **kwargs)


class ChecklistCampoLog(models.Model):
    checklist = models.ForeignKey(
        ChecklistCampo, on_delete=models.CASCADE, related_name="logs"
    )
    data_alteracao = models.DateTimeField(auto_now=True)
    campo_alterado = models.CharField(max_length=100)
    valor_antigo = models.TextField(null=True, blank=True)
    valor_novo = models.TextField(null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Log de {self.checklist} em {self.data_alteracao} por {self.usuario}"


class DetalhesUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15)
    endereco = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11)
    foto_perfil = models.ImageField(upload_to="perfil_fotos/", blank=True, null=True)

    def __str__(self):
        return self.usuario.username

    class Meta:
        db_table = "tab_detalhes_usuario"


class UnidadesMedida(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        db_table = "tab_unidade_medida"


class TipoParametro(models.Model):
    nome = models.CharField(max_length=50, blank=True, unique=True)
    descricao = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        db_table = "tab_tipo_parametro"


# ------------------------------------MIGRAÇÃO-----------------------------------------------------


class TabLocal(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(blank=True, null=True)
    local_latitude = models.FloatField(blank=True, null=True)
    local_longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        managed = True
        db_table = "tab_local"


class TabCampanha(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_local = models.ForeignKey(
        TabLocal, on_delete=models.CASCADE, db_column="id_local", blank=True, null=True
    )
    nome = models.CharField(blank=True, null=True)
    data_criacao = models.DateTimeField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        managed = True
        db_table = "tab_campanha"


class TabColeta(models.Model):
    data = models.DateTimeField(blank=True, null=True)
    nome = models.CharField(max_length=255, blank=True, null=True)
    id_campanha = models.ForeignKey(
        TabCampanha,
        on_delete=models.CASCADE,
        db_column="id_campanha",
        blank=True,
        null=True,
    )
    analise_bentos = models.BooleanField(blank=True, null=True)
    id_setor = models.ForeignKey(
        "TabSetor",
        on_delete=models.CASCADE,
        db_column="id_setor",
        blank=True,
        null=True,
    )
    ordem_servico = models.CharField(
        "Ordem de serviço", max_length=255, blank=True, null=True
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coletas_criadas",
    )
    atualizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coletas_atualizadas",
    )
    criado_em = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True, blank=True, null=True)
    status_id = models.ForeignKey(
        "TabStatusColeta",
        on_delete=models.CASCADE,
        db_column="status",
        blank=True,
        null=True,
        related_name="coletas",  # Adicionando related_name
    )
    observacao = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Capturar o usuário se for passado como parâmetro
        usuario = kwargs.pop("usuario", None) if "usuario" in kwargs else None

        # Verificar se é um objeto existente sendo atualizado
        is_update = self.pk is not None

        if is_update:
            # Buscar o estado anterior do objeto
            old_instance = TabColeta.objects.get(pk=self.pk)

            # Lista de campos que queremos monitorar
            campos_monitorados = [
                "data",
                "nome",
                "id_campanha_id",
                "id_setor_id",
                "ordem_servico",
                "status_id_id",
                "observacao",
                "analise_bentos",
            ]

            # Verificar mudanças em cada campo
            for campo in campos_monitorados:
                valor_antigo = getattr(old_instance, campo, None)
                valor_novo = getattr(self, campo, None)

                # Se houve mudança e temos um usuário, registrar log
                if valor_antigo != valor_novo and usuario:
                    TabLogColeta.objects.create(
                        id_coleta=self,
                        acao=f"Alteração no campo {campo}",
                        motivo=f'Valor alterado de "{valor_antigo}" para "{valor_novo}"',
                        usuario=usuario,
                    )

        # Se for uma nova coleta, gerar ordem de serviço
        if not self.ordem_servico and self.id_campanha and self.id_setor:
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            campanha_id = self.id_campanha.id
            setor = TabSetor.objects.get(id=self.id_setor.id)
            setor_abreviatura = setor.abreviatura
            raw_ordem_servico = f"{setor_abreviatura}{campanha_id}{data_hora}"
            self.ordem_servico = re.sub(r"[^A-Za-z0-9]", "", raw_ordem_servico)

        # Definir status inicial se não existir
        if not self.status_id and not is_update:
            self.status_id = TabStatusColeta.objects.get(id=1)

        # Atualizar carimbos de data/hora
        if is_update:
            self.atualizado_em = timezone.now()
            if usuario and not self.atualizado_por:
                self.atualizado_por = usuario
        else:
            if usuario and not self.criado_por:
                self.criado_por = usuario

        # Registrar criação se for um novo objeto e tiver usuário
        is_new = not is_update
        if is_new and usuario:
            result = super().save(*args, **kwargs)
            TabLogColeta.objects.create(
                id_coleta=self, acao="Coleta criada", usuario=usuario
            )
            return result

        return super().save(*args, **kwargs)

    def update(self, **kwargs):
        self.atualizado_em = timezone.now()
        self.atualizado_por = kwargs.get("usuario")
        self.save()

    class Meta:
        managed = True
        db_table = "tab_coleta"


class TabStatusColeta(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    cor = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="#6c757d",
        help_text="Código hexadecimal da cor (ex: #FF0000 para vermelho)",
    )

    def __str__(self):
        return f"{self.status}"

    class Meta:
        managed = True
        db_table = "tab_status_coleta"


class TabAmostra(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_ponto = models.ForeignKey(
        "TabPonto",
        on_delete=models.CASCADE,
        db_column="id_ponto",
        blank=True,
        null=True,
    )
    id_coleta = models.ForeignKey(
        "TabColeta",
        on_delete=models.CASCADE,
        db_column="id_coleta",
        blank=True,
        null=True,
    )
    id_frasco = models.ForeignKey(
        "TabFrasco",
        on_delete=models.CASCADE,
        db_column="id_frasco",
        blank=True,
        null=True,
    )
    etiqueta = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.etiqueta}"

    class Meta:
        managed = True
        db_table = "tab_amostra"

    def save(self, *args, **kwargs):
        # etiqueta = (
        #     f"{self.id_coleta.ordem_servico}{self.id_ponto.nome}{self.id_frasco.id}"
        # )
        # self.etiqueta = etiqueta
        super().save(*args, **kwargs)


class TabEnvio(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_amostra = models.ForeignKey(
        TabAmostra,
        on_delete=models.CASCADE,
        db_column="id_amostra",
        blank=True,
        null=True,
    )
    id_laboratorio = models.ForeignKey(
        "TabLaboratorio",
        models.CASCADE,
        db_column="id_laboratorio",
        blank=True,
        null=True,
    )
    data_envio = models.DateTimeField(blank=True, null=True)
    data_resultado = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        managed = True
        db_table = "tab_envio"


class TabFrasco(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        managed = True
        db_table = "tab_frasco"


class TabLaboratorio(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    laboratorio_descricao = models.TextField(blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    telefone = PhoneNumberField(blank=True, null=True, region="BR")

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        managed = True
        db_table = "tab_laboratorio"


class TabLogMedida(models.Model):
    id_medida = models.ForeignKey(
        "TabMedida", on_delete=models.SET_NULL, related_name="logs", null=True
    )
    campo_alterado = models.CharField(max_length=255)
    valor_antigo = models.TextField(blank=True, null=True)
    valor_novo = models.TextField(blank=True, null=True)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        medida_id = self.id_medida.id if self.id_medida else "excluída"
        return f"Log da medida {medida_id} - {self.campo_alterado} alterado em {self.data_alteracao}"

    class Meta:
        managed = True
        db_table = "tab_log_medida"
        ordering = ["-data_alteracao"]  # Mais recentes primeiro


class TabMedida(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_envio = models.ForeignKey(
        TabEnvio, on_delete=models.CASCADE, db_column="id_envio", blank=True, null=True
    )
    id_pp = models.ForeignKey(
        "TabProdxparam",
        on_delete=models.CASCADE,
        db_column="id_pp",
        blank=True,
        null=True,
    )
    valor = models.TextField(blank=True, null=True)
    input_valor = models.TextField(blank=True, null=True)
    operador = models.TextField(blank=True, null=True)
    err_valor = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.valor}"

    class Meta:
        managed = True
        db_table = "tab_medida"

    def save(self, *args, **kwargs):
        usuario = kwargs.pop("usuario", None)
        if not usuario:
            raise ValueError("User must be provided when saving TabMedida")

        if self.pk:  # Se já existe, é uma atualização
            old_instance = TabMedida.objects.get(pk=self.pk)
            campos_monitorados = ["valor", "input_valor"]

            for campo in campos_monitorados:
                valor_antigo = getattr(old_instance, campo)
                valor_novo = getattr(self, campo)

                if valor_antigo != valor_novo:
                    # Registra o log apenas se houver mudança
                    TabLogMedida.objects.create(
                        id_medida=self,
                        campo_alterado=campo,
                        valor_antigo=valor_antigo,
                        valor_novo=valor_novo,
                        usuario=usuario,
                    )

        super().save(*args, **kwargs)


class TabParam(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    param_meta_dado = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        managed = True
        db_table = "tab_param"


class TabPonto(models.Model):
    id_setor = models.ForeignKey(
        "TabSetor",
        on_delete=models.CASCADE,
        db_column="id_setor",
        blank=True,
        null=True,
    )
    id_local = models.ForeignKey(
        TabLocal, on_delete=models.CASCADE, db_column="id_local", blank=True, null=True
    )
    nome = models.CharField(blank=True, null=True)
    modalidade = models.CharField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    status = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        managed = True
        db_table = "tab_ponto"


class TabProduto(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        managed = True
        db_table = "tab_produto"


class TabProdxparam(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_param = models.ForeignKey(
        TabParam, on_delete=models.CASCADE, db_column="id_param", blank=True, null=True
    )
    id_produto = models.ForeignKey(
        TabProduto,
        on_delete=models.CASCADE,
        db_column="id_produto",
        blank=True,
        null=True,
    )
    id_serie = models.ForeignKey(
        "TabSerieClassificacao",
        models.CASCADE,
        db_column="id_serie",
        blank=True,
        null=True,
    )
    nome = models.TextField(blank=True, null=True)
    unidade = models.TextField(blank=True, null=True)
    limite_min = models.BigIntegerField(blank=True, null=True)
    limite_max = models.BigIntegerField(blank=True, null=True)
    id_frasco = models.ForeignKey(
        TabFrasco,
        on_delete=models.CASCADE,
        db_column="id_frasco",
        blank=True,
        null=True,
    )
    id_ppativacao = models.BigIntegerField(blank=True, null=True)
    status = models.BooleanField("Status", default=True, blank=True, null=True)
    ordem_visualizacao = models.IntegerField(
        default=999, null=True, blank=True, help_text="Define a ordem de exibição do parâmetro (menor = primeiro).")

    def __str__(self):
        return f'{self.nome} - {self.unidade or ""}'

    class Meta:
        managed = True
        db_table = "tab_prodxparam"


class TabSerieClassificacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        managed = True
        db_table = "tab_serie_classificacao"


class TabSetor(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(blank=True, null=True)
    id_local = models.ForeignKey(
        "TabLocal",
        on_delete=models.CASCADE,
        db_column="id_local",
        blank=True,
        null=True,
    )
    lon = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    abreviatura = models.CharField(max_length=50, blank=True, unique=False)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        managed = True
        db_table = "tab_setor"


class TabEquipe(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="responsavel_id",
        blank=True,
        null=True,
    )

    class Meta:
        managed = True
        db_table = "tab_equipes"


class TabItemChecklistColeta(models.Model):
    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True)
    item = models.CharField("Item", max_length=50, blank=True)
    prazo = models.FloatField(
        "Prazo para realização da ação em dias antes da coleta em dias",
        blank=True,
        null=True,
    )
    status = models.BooleanField("Este item está ativo?", default=False)
    observacao = models.TextField("Observação", max_length=500, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Usuário", null=True
    )

    def __str__(self):
        return f"{self.item}"

    def save(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        self.data_cadastro = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "tab_item_checklist_coleta"


class TabChecklistColeta(models.Model):
    item = models.ForeignKey(
        TabItemChecklistColeta, on_delete=models.CASCADE, related_name="itens"
    )
    id_coleta = models.ForeignKey(
        "TabColeta", on_delete=models.CASCADE, related_name="coleta"
    )
    status = models.BooleanField("Feito?", default=False)
    observacao = models.CharField("Observação", max_length=500, blank=True)

    def __str__(self):
        return f"{self.item}"

    class Meta:
        db_table = "tab_checklist_coleta"


class TabAnexoAmostra(models.Model):
    id_envio = models.ForeignKey(
        TabEnvio, on_delete=models.CASCADE, db_column="id_envio", blank=True, null=True
    )
    anexo = models.FileField(upload_to="anexos_amostras/", null=True, blank=True)
    ordem = models.IntegerField(default=0)  # Novo campo para ordenar anexos
    observacao = models.TextField(blank=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = "tab_anexo_amostra"
        ordering = ["ordem"]  # Ordena por ordem

    def __str__(self):
        return f"Anexo da amostra {self.id_amostra}"

    def save(self, *args, **kwargs):
        # Se não houver anexo e não houver observação, não salva
        if not self.anexo and not self.observacao:
            return
        super().save(*args, **kwargs)


class MetadadosPonto(models.Model):
    ACESSOS = [
        "Ponte",
        "Caiaque",
        "Margem",
    ]
    AVALIACAO = [
        (-1, "Negativo"),
        (0, "Neutro"),
        (1, "Positivo"),
    ]

    codigo_coleta = models.ForeignKey(
        TabAmostra, on_delete=models.CASCADE, related_name="metadados_campo"
    )
    acesso_ponto = models.CharField(
        max_length=50, choices=[(acesso, acesso) for acesso in ACESSOS], null=True
    )
    dragagem = models.IntegerField("Dragagem", choices=AVALIACAO, null=True)
    gigoga = models.IntegerField("Quantidade de gigoga", choices=AVALIACAO, null=True)
    odor = models.IntegerField("Odor", choices=AVALIACAO, null=True)
    fezes = models.IntegerField("Fezes", choices=AVALIACAO, null=True)
    oleo = models.IntegerField("Óleo", choices=AVALIACAO, null=True)
    residuos_solidos = models.IntegerField(
        "Resíduos Sólidos", choices=AVALIACAO, null=True
    )
    lodo = models.IntegerField("Lodo", choices=AVALIACAO, null=True)
    animais_presentes = models.IntegerField(
        "Animais Presentes", choices=AVALIACAO, null=True
    )
    pescadores = models.IntegerField("Pescadores", choices=AVALIACAO, null=True)
    contato_populacao = models.IntegerField(
        "Contato com a população", choices=AVALIACAO, null=True
    )
    observacao = models.TextField("Observações", max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.codigo_coleta}"

    class Meta:
        db_table = "tab_metadados_ponto"


class EmailTemplate(models.Model):
    nome_email = models.CharField(
        "Nome do e-mail", max_length=50, blank=True, null=True
    )
    assunto = models.CharField(
        "Assunto do e-mail", max_length=50, blank=True, null=True
    )
    texto = models.TextField("Texto do e-mail", blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        db_table = "tab_email_template"


class TabLogColeta(models.Model):
    id_coleta = models.ForeignKey(
        TabColeta, on_delete=models.CASCADE, related_name="logs"
    )
    acao = models.CharField(max_length=255)
    data = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.acao} em {self.data.strftime('%d/%m/%Y %H:%M')} por {self.usuario.username}"

    class Meta:
        managed = True
        db_table = "tab_log_coleta"
