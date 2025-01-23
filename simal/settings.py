MIDDLEWARE = [
    # ... existing middleware ...
    'simal.middleware.ContentSecurityPolicyMiddleware',
]

# Configurações de segurança
SECURE_SSL_REDIRECT = True  # Força HTTPS
SESSION_COOKIE_SECURE = True  # Cookies apenas via HTTPS
CSRF_COOKIE_SECURE = True  # CSRF cookies apenas via HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Permitir CORS para tiles do OpenStreetMap
CORS_ALLOWED_ORIGINS = [
    "https://tile.openstreetmap.org",
    "https://unpkg.com",
    "https://cdnjs.cloudflare.com",
]