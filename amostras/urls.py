
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Sistema de Controle de Amostras das Lagoas - SCALA - LAGOA VIVA"
admin.site.site_title = "SCALA - LAGOA VIVA"
admin.site.index_title = "ADM"
admin.site.name = "SCALA - LAGOA VIVA"


urlpatterns = [
    path('', include('coleta.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    
]
