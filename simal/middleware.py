class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://*.openstreetmap.org https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com https://*.openstreetmap.org https://cdnjs.cloudflare.com; "
            "img-src 'self' data: blob: https://*.openstreetmap.org https://*.tile.openstreetmap.org https://raw.githubusercontent.com https://cdnjs.cloudflare.com; "
            "font-src 'self' data: https://unpkg.com https://cdnjs.cloudflare.com; "
            "connect-src 'self' https://*.openstreetmap.org https://*.tile.openstreetmap.org https://nominatim.openstreetmap.org; "
            "frame-src 'self'; "
            "worker-src 'self' blob:;"
        )

        # Adiciona headers de segurança adicionais
        response["Content-Security-Policy"] = csp
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "SAMEORIGIN"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
