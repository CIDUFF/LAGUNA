from django.test import TestCase, Client
from django.urls import reverse
from .models import Ajuda
from .forms import AjudaForm

class AjudaViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('ajuda')

    def test_ajuda_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ajuda.html')
        self.assertIsInstance(response.context['form'], AjudaForm)

    def test_ajuda_post_valid(self):
        data = {
            'nome': 'Teste',
            'email': 'teste@example.com',
            'pergunta': 'Como faço para testar?'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ajuda.objects.filter(email='teste@example.com').exists())

    def test_ajuda_post_invalid(self):
        data = {
            'nome': '',
            'email': 'teste@example.com',
            'pergunta': 'Como faço para testar?'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Ajuda.objects.filter(email='teste@example.com').exists())
        
        
