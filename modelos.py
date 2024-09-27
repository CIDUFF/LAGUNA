# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountEmailaddress(models.Model):
    email = models.CharField(unique=True, max_length=254)
    verified = models.BooleanField()
    primary = models.BooleanField()
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailaddress'
        unique_together = (('user', 'email'),)


class AccountEmailconfirmation(models.Model):
    created = models.DateTimeField()
    sent = models.DateTimeField(blank=True, null=True)
    key = models.CharField(unique=True, max_length=64)
    email_address = models.ForeignKey(AccountEmailaddress, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailconfirmation'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class SocialaccountSocialaccount(models.Model):
    provider = models.CharField(max_length=200)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    extra_data = models.JSONField()
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)


class SocialaccountSocialapp(models.Model):
    provider = models.CharField(max_length=30)
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=191)
    secret = models.CharField(max_length=191)
    key = models.CharField(max_length=191)
    provider_id = models.CharField(max_length=200)
    settings = models.JSONField()

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp'


class SocialaccountSocialappSites(models.Model):
    id = models.BigAutoField(primary_key=True)
    socialapp = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)
    site = models.ForeignKey(DjangoSite, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp_sites'
        unique_together = (('socialapp', 'site'),)


class SocialaccountSocialtoken(models.Model):
    token = models.TextField()
    token_secret = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    account = models.ForeignKey(SocialaccountSocialaccount, models.DO_NOTHING)
    app = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialtoken'
        unique_together = (('app', 'account'),)


class TabAmostra(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_ponto = models.ForeignKey('TabPonto', models.DO_NOTHING, db_column='id_ponto', blank=True, null=True)
    id_coleta = models.ForeignKey('TabColeta', models.DO_NOTHING, db_column='id_coleta', blank=True, null=True)
    id_frasco = models.ForeignKey('TabFrasco', models.DO_NOTHING, db_column='id_frasco', blank=True, null=True)
    etiqueta = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_amostra'


class TabCampanha(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_local = models.ForeignKey('TabLocal', models.DO_NOTHING, db_column='id_local', blank=True, null=True)
    nome = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_campanha'


class TabColeta(models.Model):
    id = models.BigAutoField(primary_key=True)
    data = models.DateTimeField(blank=True, null=True)
    nome = models.TextField(blank=True, null=True)
    id_campanha = models.ForeignKey(TabCampanha, models.DO_NOTHING, db_column='id_campanha', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_coleta'


class TabEnvio(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_amostra = models.ForeignKey(TabAmostra, models.DO_NOTHING, db_column='id_amostra', blank=True, null=True)
    id_laboratorio = models.ForeignKey('TabLaboratorio', models.DO_NOTHING, db_column='id_laboratorio', blank=True, null=True)
    data_envio = models.DateTimeField(blank=True, null=True)
    data_resultado = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_envio'


class TabFrasco(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_frasco'


class TabLaboratorio(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    laboratorio_descricao = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_laboratorio'


class TabLocal(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    local_latitude = models.FloatField(blank=True, null=True)
    local_longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_local'


class TabMedida(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_envio = models.ForeignKey(TabEnvio, models.DO_NOTHING, db_column='id_envio', blank=True, null=True)
    id_pp = models.ForeignKey('TabProdxparam', models.DO_NOTHING, db_column='id_pp', blank=True, null=True)
    valor = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_medida'


class TabParam(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    param_meta_dado = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_param'


class TabPonto(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_setor = models.ForeignKey('TabSetor', models.DO_NOTHING, db_column='id_setor', blank=True, null=True)
    id_local = models.ForeignKey(TabLocal, models.DO_NOTHING, db_column='id_local', blank=True, null=True)
    nome = models.TextField(blank=True, null=True)
    modalidade = models.TextField(blank=True, null=True)
    ponto_lat = models.FloatField(blank=True, null=True)
    ponto_long = models.FloatField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'tab_ponto'


class TabProduto(models.Model):
    id = models.BigAutoField(primary_key=True)
    produto = models.TextField(blank=True, null=True)
    nome = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_produto'


class TabProdxparam(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_param = models.ForeignKey(TabParam, models.DO_NOTHING, db_column='id_param', blank=True, null=True)
    id_produto = models.ForeignKey(TabProduto, models.DO_NOTHING, db_column='id_produto', blank=True, null=True)
    id_serie = models.ForeignKey('TabSerieClassificacao', models.DO_NOTHING, db_column='id_serie', blank=True, null=True)
    nome = models.TextField(blank=True, null=True)
    unidade = models.TextField(blank=True, null=True)
    limite_min = models.BigIntegerField(blank=True, null=True)
    limite_max = models.BigIntegerField(blank=True, null=True)
    id_frasco = models.ForeignKey(TabFrasco, models.DO_NOTHING, db_column='id_frasco', blank=True, null=True)
    id_ppativacao = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_prodxparam'


class TabSerieClassificacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_serie_classificacao'


class TabSetor(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.TextField(blank=True, null=True)
    id_local = models.ForeignKey(TabLocal, models.DO_NOTHING, db_column='id_local', blank=True, null=True)
    local_long = models.FloatField(blank=True, null=True)
    local_lat = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_setor'
