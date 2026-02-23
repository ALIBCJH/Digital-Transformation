from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.models import Member, OrganizationNode

User = get_user_model()


class ModelTests(TestCase):
    """Test models are correctly configured"""

    def setUp(self):
        """Set up test data"""
        self.organization_unit = OrganizationNode.objects.create(
            name="Test Altar", code="TEST_ALTAR", depth=0, is_active=True
        )

    def test_organization_unit_creation(self):
        """Test organization unit can be created"""
        self.assertEqual(self.organization_unit.name, "Test Altar")
        self.assertEqual(self.organization_unit.level, "ALTAR")
        self.assertTrue(self.organization_unit.is_active)

    def test_member_creation(self):
        """Test member can be created"""
        member = Member.objects.create(
            full_name="Test Member",
            phone_number="+254712345678",
            gender="MALE",
            serving_department="Youth",
            home_altar=self.organization_unit,
        )
        self.assertEqual(member.full_name, "Test Member")
        self.assertEqual(member.phone_number, "+254712345678")
        self.assertTrue(member.is_active)


class APITests(APITestCase):
    """Test API endpoints"""

    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.altar = OrganizationNode.objects.create(
            name="Test Altar", code="TEST_ALTAR", depth=0, is_active=True
        )

    def test_register_user(self):
        """Test user registration endpoint"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "phone_number": "+254700000000",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post("/api/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_login_user(self):
        """Test user login endpoint"""
        # Create user first
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            phone_number="+254700000001",
        )

        # Try to login
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post("/api/login/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_altar_list_requires_authentication(self):
        """Test altar list endpoint requires authentication"""
        response = self.client.get("/api/altars/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_altar_list_with_authentication(self):
        """Test altar list endpoint with authentication"""
        # Create and authenticate user with organizational unit
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            phone_number="+254700000002",
            organizational_unit=self.altar,
        )
        self.client.force_authenticate(user=user)

        # Get altars
        response = self.client.get("/api/altars/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("altars", response.data)
        self.assertEqual(response.data["count"], 1)

    def test_member_create_requires_authentication(self):
        """Test member creation requires authentication"""
        data = {
            "full_name": "Test Member",
            "phone_number": "+254712345678",
            "gender": "MALE",
            "serving_department": "Youth",
            "home_altar": "Test Altar",
        }
        response = self.client.post("/api/members/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_member_create_with_authentication(self):
        """Test member creation with authentication"""
        # Create and authenticate user with organizational unit
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            phone_number="+254700000003",
            organizational_unit=self.altar,
        )
        self.client.force_authenticate(user=user)

        # Create member
        data = {
            "full_name": "Test Member",
            "phone_number": "+254712345678",
            "gender": "MALE",
            "serving_department": "Youth",
            "home_altar": "Test Altar",
        }
        response = self.client.post("/api/members/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("member", response.data)
        self.assertEqual(response.data["member"]["full_name"], "Test Member")
