class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com; "
            "img-src 'self' data: https://*.openstreetmap.org https://raw.githubusercontent.com https://cdnjs.cloudflare.com; "
            "font-src 'self'; "
            "connect-src 'self' https://*.openstreetmap.org; "
            "frame-src 'self';"
        )
        
        response["Content-Security-Policy"] = csp
        return response
