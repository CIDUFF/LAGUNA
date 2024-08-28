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

Ou com docker instalado:

```
docker-compose down --volumes --remove-orphans
docker-compose build --no-cache
docker-compose up
```


