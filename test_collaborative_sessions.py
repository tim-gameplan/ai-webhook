#!/usr/bin/env python3
"""
Test collaborative session features
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
WEBHOOK_URL = "https://web-production-3d53a.up.railway.app/webhook"

def test_create_session():
    """Test session creation"""
    print("=" * 60)
    print("TEST 1: Create Session")
    print("=" * 60)

    payload = {
        "type": "collaborative_session_command",
        "command": "create_session",
        "session_id": "mobile_test_001",
        "data": {
            "title": "Mobile LLM Integration Test",
            "participants": ["chatgpt", "developer"],
            "context": "Testing collaborative session features from mobile LLM"
        }
    }

    response = requests.post(
        WEBHOOK_URL,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json=payload,
        timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

    return response.status_code == 200

def test_store_memory():
    """Test memory storage"""
    print("=" * 60)
    print("TEST 2: Store Memory (Idea)")
    print("=" * 60)

    payload = {
        "type": "collaborative_session_command",
        "command": "store_memory",
        "session_id": "mobile_test_001",
        "data": {
            "type": "idea",
            "key": "carbon_tracking",
            "content": {
                "title": "Add carbon emissions tracking",
                "description": "Track CO2 emissions for all API calls to LLMs",
                "priority": "medium"
            },
            "tags": ["sustainability", "feature", "api"]
        }
    }

    response = requests.post(
        WEBHOOK_URL,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json=payload,
        timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

    return response.status_code == 200

if __name__ == "__main__":
    try:
        # Test 1: Create session
        success_1 = test_create_session()

        # Test 2: Store memory
        success_2 = test_store_memory()

        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Session Creation: {'✅ PASS' if success_1 else '❌ FAIL'}")
        print(f"Memory Storage:   {'✅ PASS' if success_2 else '❌ FAIL'}")
        print()

        if success_1 and success_2:
            print("🎉 ALL TESTS PASSED")
        else:
            print("⚠️  SOME TESTS FAILED")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
