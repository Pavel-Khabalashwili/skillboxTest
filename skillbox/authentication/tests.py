from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.contrib.auth import authenticate, login, logout
from authentication.views import logout_view, login_view

class LogoutViewTestCase(TestCase):
    def test_logout_view(self):
        user = User.objects.create_user(username='testuser', password='testpassword')

        self.client.login(username='testuser', password='testpassword')

        client = Client()
        
        response = client.get(reverse('authentication:logout'))  
        
        self.assertEqual(response.url, reverse("authentication:authentication"))
        self.assertEqual(response.status_code, 302) 
        
class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('authentication:authentication')

    def test_login_valid_credentials(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertRedirects(response, reverse('shop:products-list'))