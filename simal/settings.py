import os
from dotenv import load_dotenv

load_dotenv()

INSTALLED_APPS = [
    # ...existing apps...
    'django_bootstrap5',
    'django_tables2',
    'crispy_forms',
    'crispy_bootstrap5',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    # ... existing middleware ...
    "simal.middleware.ContentSecurityPolicyMiddleware",
]

# Configurações de segurança - usando valores do .env
DEBUG = os.getenv("DEBUG", "False") == "True"
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True") == "True"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "True") == "True"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True") == "True"
)
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "True") == "True"

# Permitir CORS para tiles do OpenStreetMap
CORS_ALLOWED_ORIGINS = [
    "https://tile.openstreetmap.org",
    "https://unpkg.com",
    "https://cdnjs.cloudflare.com",
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'simal/static'),
]

# Remover completamente a seção LOGGING daqui, pois já está definida no settings principal
