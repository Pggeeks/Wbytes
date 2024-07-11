from django.test import TestCase
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserManagerTestCase(TestCase):
    
    def test_create_user(self):
        """Test creating a new user"""
        email = 'test@example.com'
        username = 'testuser'
        password = 'testpass123'
        user = CustomUser.objects.create_user(email=email, username=username, password=password)
        
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.date_joined)
        self.assertIsNone(user.last_login)
        
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email='', username=username, password=password)
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email=email, username='', password=password)
        
    def test_create_superuser(self):
        """Test creating a new superuser"""
        email = 'superuser@example.com'
        username = 'superadmin'
        password = 'superpass123'
        superuser = CustomUser.objects.create_superuser(email=email, username=username, password=password)
        
        self.assertEqual(superuser.email, email)
        self.assertEqual(superuser.username, username)
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertIsNotNone(superuser.date_joined)
        self.assertIsNone(superuser.last_login)
        
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(email=email, username='', password=password)
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(email='', username=username, password=password)
