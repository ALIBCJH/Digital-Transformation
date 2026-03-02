from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

# Assuming Altar is imported from core.models
from core.models import Altar, Member, OrganizationNode

User = get_user_model()


class ModelTests(TestCase):
    """Test models are correctly configured"""

    def setUp(self):
        """Set up test data"""
        self.organization_unit = OrganizationNode.objects.create(
            name="Test Region",
            code="TEST_REGION",
            path="/TEST_REGION/",
            depth=1,
            is_active=True,
        )

        self.altar = Altar.objects.create(
            name="Test Altar",
            code="TEST_ALTAR",
            parent_node=self.organization_unit,
            is_active=True,
        )

    def test_organization_unit_creation(self):
        """Test organization unit can be created"""
        self.assertEqual(self.organization_unit.name, "Test Region")
        self.assertEqual(self.organization_unit.path, "/TEST_REGION/")
        self.assertTrue(self.organization_unit.is_active)

    def test_member_creation(self):
        """Test member can be created"""
        member = Member.objects.create(
            full_name="Test Member",
            phone_number="+254712345678",
            gender="MALE",
            home_altar=self.altar,
        )
        self.assertEqual(member.full_name, "Test Member")
        self.assertEqual(member.phone_number, "+254712345678")
        self.assertTrue(member.is_active)


class APITests(APITestCase):
    """Test API endpoints"""

    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.org_node = OrganizationNode.objects.create(
            name="Test Region",
            code="TEST_REGION",
            path="/TEST_REGION/",
            depth=1,
            is_active=True,
        )
        self.altar = Altar.objects.create(
            name="Test Altar",
            code="TEST_ALTAR",
            parent_node=self.org_node,
            is_active=True,
        )

    def test_register_user(self):
        """Test user registration endpoint"""
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email_or_phone": "test@example.com",
            "altar": "TEST_ALTAR",
            "password": "testpass123",
            "password2": "testpass123",
        }
        response = self.client.post("/api/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)

    def test_login_user(self):
        """Test user login endpoint"""
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            phone_number="+254700000001",
        )

        data = {"email_or_phone": "test@example.com", "password": "testpass123"}
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
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            phone_number="+254700000002",
        )
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/altars/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("altars", response.data)

    def test_member_create_requires_authentication(self):
        """Test member creation requires authentication"""
        data = {
            "full_name": "Test Member",
            "phone_number": "+254712345678",
            "gender": "MALE",
            "serving_department": "Youth",
            "home_altar": "TEST_ALTAR",
        }
        response = self.client.post("/api/members/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_member_create_with_authentication(self):
        """Test member creation with authentication"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            phone_number="+254700000003",
        )
        self.client.force_authenticate(user=user)

        data = {
            "full_name": "Test Member",
            "phone_number": "+254712345678",
            "gender": "MALE",
            "serving_department": "Youth",
            "home_altar": "TEST_ALTAR",
        }
        response = self.client.post("/api/members/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("member", response.data)
        self.assertEqual(response.data["member"]["full_name"], "Test Member")
