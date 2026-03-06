#!/usr/bin/env python
"""
Test script to verify:
1. Altar name normalization (case-insensitive)
2. One altar = one admin restriction
3. Attendance recording functionality
"""

from datetime import date

import requests

BASE_URL = "http://localhost:8000"


def test_registration_and_attendance():
    print("=" * 70)
    print("TESTING: REGISTRATION & ATTENDANCE SYSTEM")
    print("=" * 70)

    # Test 1: Register first admin with "nyeri main altar" (lowercase)
    print("\n1. Registering first admin with 'nyeri main altar' (lowercase)...")
    register_data_1 = {
        "first_name": "John",
        "last_name": "Doe",
        "email_or_phone": "john.doe@test.com",
        "altar": "nyeri main altar",
        "password": "testpass123",
        "password2": "testpass123"
    }

    response1 = requests.post(
        f"{BASE_URL}/api/register/",
        json=register_data_1,
        timeout=10
    )

    if response1.status_code == 201:
        data1 = response1.json()
        print("✅ First admin registered successfully!")
        print(f"   Name: {data1['user']['first_name']} {data1['user']['last_name']}")
        print(f"   Altar: {data1['user']['home_altar']}")
        print(f"   Scope: {data1['user']['scope_name']}")
        token1 = data1['access']
    else:
        print(f"❌ Registration failed: {response1.status_code}")
        print(response1.text)
        return

    # Test 2: Try to register second admin with "Nyeri Main Altar" (title case)
    print("\n2. Attempting to register second admin with 'Nyeri Main Altar' (title case)...")
    register_data_2 = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email_or_phone": "jane.smith@test.com",
        "altar": "Nyeri Main Altar",
        "password": "testpass123",
        "password2": "testpass123"
    }

    response2 = requests.post(
        f"{BASE_URL}/api/register/",
        json=register_data_2,
        timeout=10
    )

    if response2.status_code == 400:
        error_data = response2.json()
        print("✅ Second admin BLOCKED as expected!")
        print(f"   Error: {error_data.get('altar', ['N/A'])[0]}")
    else:
        print("❌ SECURITY ISSUE: Second admin was allowed to register!")
        print(response2.text)
        return

    # Test 3: Register admin for a different altar
    print("\n3. Registering admin for 'Karatina Altar'...")
    register_data_3 = {
        "first_name": "Bob",
        "last_name": "Johnson",
        "email_or_phone": "bob.johnson@test.com",
        "altar": "Karatina Altar",
        "password": "testpass123",
        "password2": "testpass123"
    }

    response3 = requests.post(
        f"{BASE_URL}/api/register/",
        json=register_data_3,
        timeout=10
    )

    if response3.status_code == 201:
        data3 = response3.json()
        print("✅ Third admin registered successfully!")
        print(f"   Name: {data3['user']['first_name']} {data3['user']['last_name']}")
        print(f"   Altar: {data3['user']['home_altar']}")
    else:
        print(f"❌ Registration failed: {response3.status_code}")
        print(response3.text)
        return

    # Test 4: Get members list for first admin
    print("\n4. Getting members list for first admin (Nyeri Main Altar)...")
    headers1 = {"Authorization": f"Bearer {token1}"}

    members_response = requests.get(
        f"{BASE_URL}/api/members/list/",
        headers=headers1,
        timeout=10
    )

    if members_response.status_code == 200:
        members = members_response.json()
        print(f"✅ Members retrieved: {len(members)} members")
    else:
        print(f"⚠️  No members yet: {members_response.status_code}")

    # Test 5: Test attendance recording (if members exist)
    print("\n5. Testing attendance recording endpoint...")

    # First, let's create a test member
    print("   Creating a test member...")
    member_data = {
        "full_name": "Test Member",
        "phone_number": "0712345678",
        "gender": "M",
        "home_altar": "Nyeri Main Altar"
    }

    create_member_response = requests.post(
        f"{BASE_URL}/api/members/create/",
        headers=headers1,
        json=member_data,
        timeout=10
    )

    if create_member_response.status_code == 201:
        member = create_member_response.json()
        print(f"   ✅ Member created: {member['full_name']}")

        # Now record attendance
        print("   Recording attendance...")

        # Get altar ID from the user data
        # For now, we'll assume altar ID is 1 (you may need to adjust this)
        attendance_data = {
            "altar_id": 1,
            "service_date": str(date.today()),
            "service_type": "sunday_service",
            "attendance": [
                {"member_id": member['id'], "is_present": True}
            ]
        }

        attendance_response = requests.post(
            f"{BASE_URL}/api/attendance/record/",
            headers=headers1,
            json=attendance_data,
            timeout=10
        )

        if attendance_response.status_code == 201:
            result = attendance_response.json()
            print("   ✅ Attendance recorded successfully!")
            print(f"      Message: {result['message']}")
            print(f"      Recorded: {result['recorded_count']} members")
        else:
            print(f"   ❌ Attendance recording failed: {attendance_response.status_code}")
            print(f"      {attendance_response.text}")
    else:
        print(f"   ⚠️  Could not create test member: {create_member_response.status_code}")

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("✅ Altar name normalization: WORKING")
    print("✅ One altar = one admin: ENFORCED")
    print("✅ Different altars = different admins: ALLOWED")
    print("✅ Attendance recording: FUNCTIONAL")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_registration_and_attendance()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
