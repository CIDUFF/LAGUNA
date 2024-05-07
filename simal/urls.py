from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('coleta/', views.coleta, name='coleta'),
    
    
    path('lista_coleta/', views.lista_coleta, name='lista_coleta'),
    path('atualizar_coleta/<int:id>/', views.atualizar_coleta, name='atualizar_coleta'),
]