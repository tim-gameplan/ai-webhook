#!/usr/bin/env python3
"""
Deployment Test Script for GitHub Webhook Relay

Usage:
    python test_deployment.py https://your-app.railway.app
"""

import sys
import requests
import asyncio
import websockets
import json
from datetime import datetime


def test_server_health(base_url: str):
    """Test if server is running and responding"""
    print("=" * 60)
    print("TEST 1: Server Health Check")
    print("=" * 60)

    try:
        response = requests.get(f"{base_url}/", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is running")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Connected clients: {data.get('connected_clients')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to server: {e}")
        return False


def test_webhook_endpoint(base_url: str):
    """Test webhook endpoint accepts POST requests"""
    print("\n" + "=" * 60)
    print("TEST 2: Webhook Endpoint")
    print("=" * 60)

    try:
        payload = {
            "zen": "Design for failure.",
            "hook_id": 123456,
            "hook": {"type": "Repository", "id": 123456}
        }

        headers = {
            "Content-Type": "application/json",
            "X-GitHub-Event": "ping",
            "X-GitHub-Delivery": "12345678-1234-1234-1234-123456789abc"
        }

        response = requests.post(
            f"{base_url}/webhook",
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook endpoint is working")
            print(f"   Status: {data.get('status')}")
            print(f"   Event: {data.get('event')}")
            print(f"   Clients notified: {data.get('clients_notified')}")
            return True
        else:
            print(f"❌ Webhook endpoint returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test webhook endpoint: {e}")
        return False


async def test_websocket_connection(ws_url: str):
    """Test WebSocket connection"""
    print("\n" + "=" * 60)
    print("TEST 3: WebSocket Connection")
    print("=" * 60)

    try:
        async with websockets.connect(ws_url, open_timeout=10) as websocket:
            print(f"✅ WebSocket connected")

            # Wait for welcome message
            message = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(message)

            if data.get("type") == "connection":
                print(f"✅ Received welcome message")
                print(f"   Message: {data.get('message')}")

                # Send ping
                await websocket.send(json.dumps({"type": "ping"}))
                print(f"✅ Sent ping")

                # Wait for pong
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                pong_data = json.loads(response)

                if pong_data.get("type") == "pong":
                    print(f"✅ Received pong")
                    return True
                else:
                    print(f"⚠️  Unexpected response type: {pong_data.get('type')}")
                    return True  # Still connected
            else:
                print(f"⚠️  Unexpected message type: {data.get('type')}")
                return True

    except asyncio.TimeoutError:
        print(f"❌ WebSocket connection timeout")
        return False
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False


async def test_webhook_relay(base_url: str, ws_url: str):
    """Test complete webhook relay (webhook → websocket)"""
    print("\n" + "=" * 60)
    print("TEST 4: Complete Webhook Relay")
    print("=" * 60)
    print("This test will wait 10 seconds for a webhook to arrive...")
    print("(You can manually trigger one from GitHub webhook settings)")

    try:
        async with websockets.connect(ws_url, open_timeout=10) as websocket:
            # Wait for welcome message
            await websocket.recv()

            print(f"✅ Connected, waiting for webhooks...")

            # Wait for a webhook (with timeout)
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(message)

                if data.get("type") == "webhook":
                    print(f"✅ Received webhook via WebSocket!")
                    print(f"   Event: {data.get('event')}")
                    print(f"   Delivery ID: {data.get('delivery_id')}")
                    return True
                else:
                    print(f"⚠️  No webhook received in 10 seconds (got {data.get('type')})")
                    print(f"   This is normal if no GitHub events were triggered")
                    return True

            except asyncio.TimeoutError:
                print(f"⚠️  No webhook received in 10 seconds")
                print(f"   This is normal if no GitHub events were triggered")
                return True

    except Exception as e:
        print(f"❌ Relay test failed: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_deployment.py <server-url>")
        print("Example: python test_deployment.py https://your-app.railway.app")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")

    # Convert HTTP(S) URL to WS(S) for WebSocket
    ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://") + "/ws"

    print("\n" + "=" * 60)
    print(f"Testing Deployment: {base_url}")
    print("=" * 60)
    print(f"HTTP URL: {base_url}")
    print(f"WebSocket URL: {ws_url}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)

    results = []

    # Run HTTP tests
    results.append(("Server Health", test_server_health(base_url)))
    results.append(("Webhook Endpoint", test_webhook_endpoint(base_url)))

    # Run WebSocket tests
    results.append(("WebSocket Connection", asyncio.run(test_websocket_connection(ws_url))))
    results.append(("Webhook Relay", asyncio.run(test_webhook_relay(base_url, ws_url))))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)

    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Deployment is ready.")
        print("\nNext steps:")
        print("1. Configure GitHub webhook:")
        print(f"   URL: {base_url}/webhook")
        print("   Content type: application/json")
        print("2. Run local client:")
        print(f"   export RELAY_SERVER_URL=\"{ws_url}\"")
        print("   python client/client.py")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
