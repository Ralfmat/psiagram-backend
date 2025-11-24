from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('custom_register')
        self.login_url = '/api/v1/auth/login/'
        self.user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPassword123!'
        }

    def test_registration(self):
        """Registration test for a new user."""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'newuser')

    def test_login(self):
        """Test for logging into a registered account."""
        User.objects.create_user(
            username='login_user',
            email='login@example.com',
            password='MyPassword123'
        )

        data = {
            'username': 'login_user',
            'password': 'MyPassword123',
            'email': 'login@example.com' 
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn('access', response.data)
        self.assertTrue(len(response.data['access']) > 0)