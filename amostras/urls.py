
from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls

admin.site.site_header = "Sistema de Monitoramento Integrado de Águas Lagunares "
admin.site.site_title = "SCALA - LAGOA VIVA"
admin.site.index_title = "ADM"
admin.site.name = "SIMAL - LAGOA VIVA"


urlpatterns = [
    path('', include('simal.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    
] + debug_toolbar_urls()
