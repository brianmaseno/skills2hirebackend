"""
Tests for accounts app
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration"""
    
    def test_register_job_seeker(self):
        """Test registering a job seeker"""
        client = APIClient()
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'user_type': 'job_seeker'
        }
        response = client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='newuser@example.com').exists()
        assert 'user' in response.data
    
    def test_register_employer(self):
        """Test registering an employer"""
        client = APIClient()
        data = {
            'email': 'employer@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'user_type': 'employer'
        }
        response = client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email='employer@example.com')
        assert user.is_employer
    
    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        client = APIClient()
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'different',
            'user_type': 'job_seeker'
        }
        response = client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAuthentication:
    """Test JWT authentication"""
    
    def test_login_success(self, job_seeker_user):
        """Test successful login"""
        client = APIClient()
        data = {
            'email': 'jobseeker@example.com',
            'password': 'testpass123'
        }
        response = client.post('/api/auth/token/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        client = APIClient()
        data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpass'
        }
        response = client.post('/api/auth/token/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
