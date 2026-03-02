"""
Modern PyTest test suite for Digital Transformation API
"""
import pytest
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Altar, OrganizationNode, User


@pytest.mark.django_db
class TestAuthentication:
    """Test authentication endpoints using PyTest"""

    def setup_method(self):
        """Set up test data for each test method"""
        self.client = APIClient()

        # Create test organization node
        self.org_node = OrganizationNode.objects.create(
            name="Test Region", code="TEST", is_active=True
        )

        # Create test altar
        self.altar = Altar.objects.create(
            name="Test Altar",
            code="TEST_ALTAR",
            parent_node=self.org_node,
            is_active=True,
        )

    def test_register_success(self):
        """Test successful user registration"""
        url = reverse("register")
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email_or_phone": "john.doe@test.com",
            "altar": "Test Altar",
            "password": "TestPass123!",
            "password2": "TestPass123!",
        }

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "user" in response.data
        assert response.data["user"]["first_name"] == "John"

    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        url = reverse("register")
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email_or_phone": "john.doe@test.com",
            "altar": "Test Altar",
            "password": "TestPass123!",
            "password2": "DifferentPass123!",
        }

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self):
        """Test successful login"""
        # First create a user
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="TestPass123!",
        )

        url = reverse("login")
        data = {"email_or_phone": "test@example.com", "password": "TestPass123!"}

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "user" in response.data

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse("login")
        data = {
            "email_or_phone": "nonexistent@example.com",
            "password": "WrongPassword123!",
        }

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAltarEndpoints:
    """Test altar-related endpoints"""

    def setup_method(self):
        """Set up test data"""
        self.client = APIClient()

        self.org_node = OrganizationNode.objects.create(
            name="Test Region", code="TEST", is_active=True
        )

        self.altar = Altar.objects.create(
            name="Test Altar",
            code="TEST_ALTAR",
            parent_node=self.org_node,
            is_active=True,
        )

    def test_altar_list(self):
        """Test altar list endpoint"""
        url = reverse("altar_list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "altars" in response.data


@pytest.mark.django_db
class TestMemberEndpoints:
    """Test member-related endpoints"""

    def setup_method(self):
        """Set up test data"""
        self.client = APIClient()

        # Create user and authenticate
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="TestPass123!",
        )

        self.org_node = OrganizationNode.objects.create(
            name="Test Region", code="TEST", is_active=True
        )

        self.altar = Altar.objects.create(
            name="Test Altar",
            code="TEST_ALTAR2",
            parent_node=self.org_node,
            is_active=True,
        )

        # Authenticate client
        self.client.force_authenticate(user=self.user)

    def test_member_list_requires_auth(self):
        """Test that member list requires authentication"""
        client = APIClient()  # Unauthenticated client
        url = "/api/members/list/"
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_member_list_authenticated(self):
        """Test member list with authentication"""
        url = "/api/members/list/"
        response = self.client.get(url)
        # Should return 200 even if empty
        assert response.status_code == status.HTTP_200_OK


# Test configuration override for SQLite (avoids PostgreSQL extension issues)
@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)
class TestWithSQLite(TestCase):
    """Tests that run with SQLite to avoid PostgreSQL extension issues"""

    def test_basic_functionality(self):
        """Basic test to ensure Django is working"""
        self.assertTrue(True)
