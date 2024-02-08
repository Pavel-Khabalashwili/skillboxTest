from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class RegisterViewTest(TestCase):
    def test_register_view(self):
        url = reverse("register:register")
        data = {
            "username": "testuser",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(User.objects.filter(username="testuser").exists())
        
        user = User.objects.get(username="testuser")
        self.assertTrue(user.is_authenticated)