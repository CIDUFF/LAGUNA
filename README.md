# LAGUNA

Laboratório Avançado para Gerenciamento, Uso e Análise de Amostras


## Descrição

Para rodar o sistema, é necessário ter o Python 3.6 ou superior instalado.

Crie o ambiente virtual:

```bash
python -m venv venv
```

Para ativar o ambiente virtual, execute o comando:

linux:
```bash
source venv/bin/activate
```

windows:
```bash
venv\Scripts\activate
```

Para instalar as dependências, execute o comando:

```bash
pip install -r requirements.txt
```

Para rodar o sistema, execute o comando:

```bash
python manage.py runserver
```

para gerar o diagrama ER dos modelos, execute o comando:

```bash
python manage.py graph_models simal -o EntidadeRelacionamento.png
```

ou 

```bash
uv run ./manage.py graph_models simal | dot -Tpdf -o output.pdf
evince output.pdf
```	


<!-- Não usar docker -->
<!-- Ou com docker instalado: -->

<!-- ```
docker-compose down --volumes --remove-orphans
docker-compose build --no-cache
docker-compose up
``` -->

<!-- reiniciar sequencia de id:

SELECT setval(pg_get_serial_sequence('tab_nome_tabela', 'id'), COALESCE((SELECT MAX(id) FROM tab_ponto), 1), true); -->

## Documentação

Em tabelas que foram populadas com dump de dados de excel e outros sistemas, é possível que o id_seq não esteja correto, para corrigir isso, execute o comando sql:

```sql
SELECT setval('nomedatabela_id_seq', (SELECT MAX(id) FROM nomedatabela)+1);
```


<!-- sudo /etc/init.d/apache2 reload -->

<!-- /var/log/django/amostras.log -->

reset da sequenccia sql

uv run ./manage.py sqlsequencereset simal

# comandos do django

Comandos Django Padrão
check: Verifica a integridade do projeto Django.
compilemessages: Compila arquivos de mensagens .po para .mo.
createcachetable: Cria uma tabela de cache no banco de dados.
dbshell: Abre um shell do banco de dados.
diffsettings: Mostra as diferenças entre as configurações padrão e as configurações atuais.
dumpdata: Exporta dados do banco de dados para um arquivo.
flush: Remove todos os dados do banco de dados e reinicia os IDs das tabelas.
inspectdb: Gera modelos Django a partir de um banco de dados existente.
loaddata: Carrega dados de um arquivo para o banco de dados.
makemessages: Cria arquivos de mensagens .po para tradução.
makemigrations: Cria novas migrações com base nas mudanças nos modelos.
migrate: Aplica migrações ao banco de dados.
sendtestemail: Envia um email de teste.
shell: Abre um shell interativo do Django.
showmigrations: Mostra todas as migrações e seu status.
sqlflush: Mostra as instruções SQL que serão executadas pelo comando flush.
sqlmigrate: Mostra as instruções SQL para uma migração específica.
sqlsequencereset: Mostra as instruções SQL para redefinir sequências de tabelas.
squashmigrations: Combina várias migrações em uma única migração.
startapp: Cria uma nova aplicação Django.
startproject: Cria um novo projeto Django.
test: Executa os testes do projeto.
testserver: Executa um servidor de desenvolvimento com dados de teste.
Comandos Django Extensions
admin_generator: Gera código para o admin do Django.
clean_pyc: Remove arquivos .pyc.
clear_cache: Limpa o cache.
compile_pyc: Compila arquivos .py para .pyc.
create_command: Cria um novo comando de gerenciamento.
create_jobs: Cria jobs para o Django.
create_template_tags: Cria tags de template.
delete_squashed_migrations: Deleta migrações combinadas.
describe_form: Descreve um formulário.
drop_test_database: Remove o banco de dados de teste.
dumpscript: Exporta dados do banco de dados para um script Python.
export_emails: Exporta emails dos usuários.
find_template: Encontra templates.
generate_password: Gera uma senha.
generate_secret_key: Gera uma chave secreta.
graph_models: Gera um gráfico dos modelos.
list_model_info: Lista informações dos modelos.
list_signals: Lista sinais do Django.
mail_debug: Envia um email de depuração.
managestate: Gerencia o estado do projeto.
merge_model_instances: Mescla instâncias de modelos.
notes: Mostra notas do código.
pipchecker: Verifica pacotes pip desatualizados.
print_settings: Imprime as configurações do Django.
print_user_for_session: Imprime o usuário para uma sessão.
raise_test_exception: Levanta uma exceção de teste.
reset_db: Reseta o banco de dados.
reset_schema: Reseta o esquema do banco de dados.
runjob: Executa um job.
runjobs: Executa jobs.
runprofileserver: Executa o servidor de perfil.
runscript: Executa um script.
runserver_plus: Executa o servidor de desenvolvimento com funcionalidades adicionais.
set_default_site: Define o site padrão.
set_fake_emails: Define emails falsos.
set_fake_passwords: Define senhas falsas.
shell_plus: Abre um shell interativo com funcionalidades adicionais.
show_template_tags: Mostra tags de template.
show_urls: Mostra URLs do projeto.
sqlcreate: Mostra instruções SQL para criar o banco de dados.
sqldiff: Mostra diferenças entre o esquema do banco de dados e os modelos.
sqldsn: Mostra a string de conexão do banco de dados.
sync_s3: Sincroniza arquivos com o S3.
syncdata: Sincroniza dados.
unreferenced_files: Mostra arquivos não referenciados.
update_permissions: Atualiza permissões.
validate_templates: Valida templates.
Comandos de Sessões
clearsessions: Limpa sessões expiradas.
Comandos de Arquivos Estáticos
collectstatic: Coleta arquivos estáticos em um único local.
findstatic: Encontra arquivos estáticos.
runserver: Executa o servidor de desenvolvimento.