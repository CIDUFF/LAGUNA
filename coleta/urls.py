from django.urls import path, include
from . import views

urlpatterns = [
    
    path('coleta/', views.coleta, name='coleta'),
    
]