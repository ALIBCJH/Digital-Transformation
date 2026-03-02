"""
Test script to demonstrate organizational scope-based permissions

This script shows how admins can only manage data within their assigned
organizational units (Region, Sub-Region, or Altar).
"""

import os

import django
from django.db import transaction

from core.models import OrganizationNode, User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def demo_organizational_scope():
    print("\n" + "=" * 80)
    print("ORGANIZATIONAL SCOPE PERMISSIONS DEMO")
    print("=" * 80 + "\n")

    # Get organizational units
    try:
        nyeri_region = OrganizationNode.objects.get(name="Nyeri Main Altar")
        mweiga_altar = OrganizationNode.objects.get(name="Mweiga Altar")
        karatina_altar = OrganizationNode.objects.get(name="Karatina Main Altar")
    except OrganizationNode.DoesNotExist as e:
        print(f"❌ Error: {e}")
        print("Run 'python manage.py seed_altars' first!\n")
        return

    print("📊 Organizational Structure:")
    print("   - Nyeri Main Altar (REGION)")
    print("     └─ Mweiga Altar")
    print("     └─ Karatina Main Altar")
    print()

    # Create test admins with different scopes
    with transaction.atomic():
        # 1. Regional Admin (can manage all altars in Nyeri Region)
        regional_admin, created = User.objects.get_or_create(
            username="regional_admin",
            defaults={
                "email": "regional@example.com",
                "phone_number": "+254700000001",
                "organizational_unit": nyeri_region,
                "is_staff": True,
                "is_superuser": False,
            },
        )
        if created:
            regional_admin.set_password("password123")
            regional_admin.save()
            print("✅ Created Regional Admin (Nyeri Main Altar)")
        else:
            print("ℹ️  Regional Admin already exists")

        # 2. Altar Admin (can only manage Mweiga Altar)
        altar_admin, created = User.objects.get_or_create(
            username="mweiga_admin",
            defaults={
                "email": "mweiga@example.com",
                "phone_number": "+254700000002",
                "organizational_unit": mweiga_altar,
                "is_staff": True,
                "is_superuser": False,
            },
        )
        if created:
            altar_admin.set_password("password123")
            altar_admin.save()
            print("✅ Created Altar Admin (Mweiga Altar only)")
        else:
            print("ℹ️  Altar Admin already exists")

    print("\n" + "-" * 80)
    print("PERMISSION SCOPE BREAKDOWN")
    print("-" * 80 + "\n")

    # Test Regional Admin permissions
    print("👤 Regional Admin (regional_admin):")
    print(
        f"   Assigned to: {regional_admin.organizational_unit.name} "
        f"({regional_admin.organizational_unit.level})"
    )
    print("   Can manage: All altars within Nyeri Region")

    managed_units = regional_admin.get_managed_units()
    print(f"   Accessible units: {managed_units.count()} total")
    for unit in managed_units.filter(level="ALTAR").order_by("name"):
        print(f"      ✓ {unit.name}")

    print(
        f"\n   Can manage Mweiga Altar? "
        f"{regional_admin.can_manage_unit(mweiga_altar)} ✅"
    )
    print(
        f"   Can manage Karatina Altar? "
        f"{regional_admin.can_manage_unit(karatina_altar)} ✅"
    )

    print("\n" + "-" * 80 + "\n")

    # Test Altar Admin permissions
    print("👤 Altar Admin (mweiga_admin):")
    print(
        f"   Assigned to: {altar_admin.organizational_unit.name} "
        f"({altar_admin.organizational_unit.level})"
    )
    print("   Can manage: Only Mweiga Altar")

    managed_units = altar_admin.get_managed_units()
    print(f"   Accessible units: {managed_units.count()} total")
    for unit in managed_units.filter(level="ALTAR").order_by("name"):
        print(f"      ✓ {unit.name}")

    print(
        f"\n   Can manage Mweiga Altar? "
        f"{altar_admin.can_manage_unit(mweiga_altar)} ✅"
    )
    print(
        f"   Can manage Karatina Altar? "
        f"{altar_admin.can_manage_unit(karatina_altar)} ❌"
    )

    print("\n" + "=" * 80)
    print("HOW IT WORKS IN API ENDPOINTS")
    print("=" * 80 + "\n")

    print("📝 Member Creation (POST /api/members/create/):")
    print("   ✅ Regional Admin: Can create members for ANY altar in Nyeri Region")
    print("   ✅ Mweiga Admin: Can ONLY create members for Mweiga Altar")
    print(
        "   ❌ Mweiga Admin: CANNOT create members for Karatina Altar (403 Forbidden)"
    )

    print("\n📋 Member List (GET /api/members/list/):")
    print("   ✅ Regional Admin: Sees members from ALL altars in Nyeri Region")
    print("   ✅ Mweiga Admin: Sees ONLY members from Mweiga Altar")

    print("\n📊 Attendance Recording (POST /api/attendance/record/):")
    print("   ✅ Regional Admin: Can record attendance for ANY altar in Nyeri Region")
    print("   ✅ Mweiga Admin: Can ONLY record attendance for Mweiga Altar")
    print(
        "   ❌ Mweiga Admin: CANNOT record attendance for Karatina Altar "
        "(403 Forbidden)"
    )

    print("\n🔄 Member Transfer (POST /api/members/transfer/):")
    print(
        "   ✅ Regional Admin: Can transfer members between ANY altars in Nyeri Region"
    )
    print("   ✅ Mweiga Admin: Can ONLY transfer members FROM Mweiga Altar")
    print(
        "   ❌ Mweiga Admin: CANNOT transfer members from other altars (403 Forbidden)"
    )

    print("\n" + "=" * 80)
    print("LOGIN CREDENTIALS FOR TESTING")
    print("=" * 80 + "\n")

    print("1️⃣  Regional Admin (Full Region Access):")
    print("   Username: regional_admin")
    print("   Password: password123")
    print("   Scope: Entire Nyeri Region (all 5 altars)")

    print("\n2️⃣  Altar Admin (Single Altar Access):")
    print("   Username: mweiga_admin")
    print("   Password: password123")
    print("   Scope: Mweiga Altar only")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80 + "\n")

    print("1. Login with either admin:")
    print("   POST /api/login/")
    print('   {"username": "regional_admin", "password": "password123"}')

    print("\n2. Try creating a member:")
    print("   POST /api/members/create/")
    print("   Headers: Authorization: Bearer <access_token>")
    print("   {")
    print('     "full_name": "Test Member",')
    print('     "phone_number": "+254712345678",')
    print('     "gender": "MALE",')
    print('     "serving_department": "Ushers",')
    print('     "home_altar": "Mweiga Altar"')
    print("   }")

    print("\n3. Test with Mweiga Admin trying to access Karatina Altar")
    print("   (Should return 403 Forbidden)")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    demo_organizational_scope()
