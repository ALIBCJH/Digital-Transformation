#!/usr/bin/env python
"""
Script to test the bulk attendance recording endpoint
"""
import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000"

def main():
    # Step 1: Login to get access token
    print("1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/login/",
        json={"username": "admin", "password": "admin12345"},
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    access_token = login_response.json()["access"]
    print(f"✅ Login successful, token: {access_token[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get members for attendance
    print("\n2. Getting members for attendance...")
    members_response = requests.get(
        f"{BASE_URL}/api/attendance/members/",
        headers=headers,
        params={"altar_id": 1}
    )
    
    if members_response.status_code != 200:
        print(f"❌ Failed to get members: {members_response.status_code}")
        print(members_response.text)
        return
    
    members_data = members_response.json()
    print(f"✅ Got {len(members_data['members'])} members")
    print(f"   Altar: {members_data['altar_name']}")
    
    # Step 3: Record attendance (mark first 2 members as present)
    print("\n3. Recording attendance...")
    present_member_ids = [m['id'] for m in members_data['members'][:2]]
    
    attendance_data = {
        "altar_id": 1,
        "service_date": str(date.today()),
        "service_type": "sunday_service",
        "attendance_records": [
            {"member_id": member_id, "is_present": True}
            for member_id in present_member_ids
        ]
    }
    
    print(f"   Marking {len(present_member_ids)} members as present")
    print(f"   Service Date: {attendance_data['service_date']}")
    print(f"   Service Type: {attendance_data['service_type']}")
    
    attendance_response = requests.post(
        f"{BASE_URL}/api/attendance/record/",
        headers=headers,
        json=attendance_data
    )
    
    if attendance_response.status_code == 201:
        result = attendance_response.json()
        print(f"✅ Attendance recorded successfully!")
        print(f"   Message: {result['message']}")
        print(f"   Recorded: {result['recorded_count']} members")
    else:
        print(f"❌ Failed to record attendance: {attendance_response.status_code}")
        print(attendance_response.text)
        return
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    main()
