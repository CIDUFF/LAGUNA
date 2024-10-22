from django.test import TestCase, Client
from django.urls import reverse
from simal.models import TabColeta, TabFrasco, TabPonto, TabAmostraCopy
from django.contrib.auth.models import User
from django.core.management import call_command


class FillAmostraTest(TestCase):
    def setUp(self):
        # Carregar dados do fixture
        call_command('loaddata', 'initial_data.json')

        # Criar um usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')

        # Criar objetos necessários
        self.coleta = TabColeta.objects.create(
            id=25, id_setor=1, id_campanha=1)
        self.frasco1 = TabFrasco.objects.create(id=1, nome='Frasco 1')
        self.frasco2 = TabFrasco.objects.create(id=2, nome='Frasco 2')
        self.ponto1 = TabPonto.objects.create(id=1, id_setor=1, nome='Ponto 1')
        self.ponto2 = TabPonto.objects.create(id=2, id_setor=1, nome='Ponto 2')

    def test_fill_amostra(self):
        response = self.client.get(reverse('fill_amostra', args=[25]))
        # Redirecionamento esperado
        self.assertEqual(response.status_code, 302)

        # Verificar se as amostras foram criadas
        amostras = TabAmostraCopy.objects.filter(id_coleta=self.coleta)
        # 2 frascos * 2 pontos = 4 amostras
        self.assertEqual(amostras.count(), 4)

        # Verificar se as amostras estão corretas
        for frasco in [self.frasco1, self.frasco2]:
            for ponto in [self.ponto1, self.ponto2]:
                self.assertTrue(TabAmostraCopy.objects.filter(
                    id_coleta=self.coleta, id_frasco=frasco, id_ponto=ponto).exists())
