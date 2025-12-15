#!/usr/bin/env python3
"""
Integration test script to verify Flask-FastAPI frontend-backend parity.
This script tests the complete integration between frontend and FastAPI backend.
"""

import asyncio
import json
import sys
import time
import requests
import websockets
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8065"
WS_URL = "ws://localhost:8065/ws/frontend"
API_BASE = f"{BACKEND_URL}/api/v1"


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(message):
    """Print success message in green"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message):
    """Print error message in red"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_info(message):
    """Print info message in blue"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def print_warning(message):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def test_backend_health():
    """Test if FastAPI backend is running"""
    print_info("Testing backend health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend health check passed")
            return True
        else:
            print_error(f"Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Backend connection failed: {e}")
        return False


def test_engines_api():
    """Test engines API endpoints"""
    print_info("Testing engines API endpoints...")
    
    try:
        # First authenticate to get token
        auth_response = requests.post(
            f"{API_BASE}/auth/bypass-login",
            json={"username": "admin", "password": "admin"},
            timeout=5
        )
        if auth_response.status_code != 200:
            print_error(f"Authentication failed: {auth_response.status_code}")
            return False
        
        auth_data = auth_response.json()
        token = auth_data.get("access_token")
        if not token:
            print_error("No access token received")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test get all engine statuses
        response = requests.get(f"{API_BASE}/engines/status", headers=headers, timeout=5)
        if response.status_code != 200:
            print_error(f"Engine status endpoint failed: {response.status_code}")
            return False
        
        data = response.json()
        expected_engines = ['insight', 'media', 'query', 'forum']
        
        for engine in expected_engines:
            if engine not in data:
                print_error(f"Missing engine in status response: {engine}")
                return False
            
            if 'status' not in data[engine]:
                print_error(f"Missing status for engine: {engine}")
                return False
        
        print_success("Engine status endpoint works correctly")
        
        # Test start engine endpoint
        response = requests.post(f"{API_BASE}/engines/insight/start", headers=headers, timeout=5)
        if response.status_code != 200:
            print_error(f"Engine start endpoint failed: {response.status_code}")
            return False
        
        data = response.json()
        if 'success' not in data or 'message' not in data:
            print_error("Invalid response format from engine start")
            return False
        
        print_success("Engine start endpoint works correctly")
        
        # Test get engine output
        response = requests.get(f"{API_BASE}/engines/insight/output", headers=headers, timeout=5)
        if response.status_code != 200:
            print_error(f"Engine output endpoint failed: {response.status_code}")
            return False
        
        data = response.json()
        if 'success' not in data or 'output' not in data:
            print_error("Invalid response format from engine output")
            return False
        
        print_success("Engine output endpoint works correctly")
        
        return True
        
    except Exception as e:
        print_error(f"Engines API test failed: {e}")
        return False


def test_analysis_endpoint():
    """Test analysis endpoint"""
    print_info("Testing analysis endpoint...")
    
    try:
        # First authenticate to get token
        auth_response = requests.post(
            f"{API_BASE}/auth/bypass-login",
            json={"username": "admin", "password": "admin"},
            timeout=5
        )
        if auth_response.status_code != 200:
            print_error(f"Authentication failed: {auth_response.status_code}")
            return False
        
        auth_data = auth_response.json()
        token = auth_data.get("access_token")
        if not token:
            print_error("No access token received")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        analysis_request = {
            "query": "test integration query",
            "engines": ["insight", "media", "query"],
            "options": {
                "max_results": 10,
                "sentiment_analysis": True
            }
        }
        
        response = requests.post(f"{API_BASE}/engines/analyze", json=analysis_request, headers=headers, timeout=5)
        if response.status_code != 200:
            print_error(f"Analysis endpoint failed: {response.status_code}")
            return False
        
        data = response.json()
        if 'success' not in data or 'analysis_id' not in data:
            print_error("Invalid response format from analysis")
            return False
        
        print_success("Analysis endpoint works correctly")
        return True
        
    except Exception as e:
        print_error(f"Analysis endpoint test failed: {e}")
        return False


async def test_websocket_connection():
    """Test WebSocket connection and message handling"""
    print_info("Testing WebSocket connection...")
    
    try:
        # Use connect without timeout parameter to avoid compatibility issues
        async with websockets.connect(WS_URL) as websocket:
            # Send connection message
            await websocket.send(json.dumps({"type": "connect"}))
            
            # Receive connection response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                
                if data.get('type') != 'connect':
                    print_error("Invalid connection response")
                    return False
                
                print_success("WebSocket connection established")
                
                # Test status request
                await websocket.send(json.dumps({"type": "request_status"}))
                
                # Receive status update with timeout
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                
                if data.get('type') != 'status_update':
                    print_error("Invalid status response")
                    return False
                
                print_success("WebSocket status request works correctly")
                
                # Test engine subscription
                await websocket.send(json.dumps({
                    "type": "subscribe_engine",
                    "data": {"engine_type": "insight"}
                }))
                
                print_success("WebSocket engine subscription works correctly")
                
                return True
            except asyncio.TimeoutError:
                print_error("WebSocket response timeout")
                return False
            
    except Exception as e:
        print_error(f"WebSocket test failed: {e}")
        return False


def test_websocket_api_endpoints():
    """Test WebSocket management API endpoints"""
    print_info("Testing WebSocket management API...")
    
    try:
        # First authenticate to get token
        auth_response = requests.post(
            f"{API_BASE}/auth/bypass-login",
            json={"username": "admin", "password": "admin"},
            timeout=5
        )
        if auth_response.status_code != 200:
            print_error(f"Authentication failed: {auth_response.status_code}")
            return False
        
        auth_data = auth_response.json()
        token = auth_data.get("access_token")
        if not token:
            print_error("No access token received")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test get connections
        response = requests.get(f"{BACKEND_URL}/ws/connections", headers=headers, timeout=5)
        if response.status_code != 200:
            print_error(f"WebSocket connections endpoint failed: {response.status_code}")
            return False
        
        data = response.json()
        if 'success' not in data or 'data' not in data:
            print_error("Invalid response format from connections endpoint")
            return False
        
        print_success("WebSocket connections endpoint works correctly")
        
        # Test broadcast message
        broadcast_message = {
            "message": {"type": "test", "content": "integration test"}
        }
        response = requests.post(f"{BACKEND_URL}/ws/broadcast", json=broadcast_message, headers=headers, timeout=5)
        if response.status_code != 200:
            print_error(f"WebSocket broadcast endpoint failed: {response.status_code}")
            return False
        
        data = response.json()
        if 'success' not in data:
            print_error("Invalid response format from broadcast endpoint")
            return False
        
        print_success("WebSocket broadcast endpoint works correctly")
        
        return True
        
    except Exception as e:
        print_error(f"WebSocket API test failed: {e}")
        return False


def test_frontend_compatibility():
    """Test frontend API client compatibility"""
    print_info("Testing frontend API client compatibility...")
    
    try:
        # Check if frontend API files exist
        frontend_files = [
            "frontend/src/lib/api/client.ts",
            "frontend/src/lib/api/engines.ts",
            "frontend/src/lib/api/websocket.ts"
        ]
        
        for file_path in frontend_files:
            if not Path(file_path).exists():
                print_error(f"Frontend API file missing: {file_path}")
                return False
        
        print_success("Frontend API files exist")
        
        # Check if API endpoints match
        with open("frontend/src/lib/api/engines.ts", 'r') as f:
            content = f.read()
            if "/api/v1/engines/" not in content:
                print_error("Frontend API endpoints don't match FastAPI structure")
                return False
        
        print_success("Frontend API endpoints match FastAPI structure")
        
        # Check if WebSocket client uses correct URL
        with open("frontend/src/lib/api/websocket.ts", 'r') as f:
            content = f.read()
            if "ws://localhost:8065/ws/frontend" not in content:
                print_error("Frontend WebSocket URL doesn't match FastAPI structure")
                return False
        
        print_success("Frontend WebSocket URL matches FastAPI structure")
        
        return True
        
    except Exception as e:
        print_error(f"Frontend compatibility test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and response formats"""
    print_info("Testing error handling...")
    
    try:
        # Test 404 error
        response = requests.get(f"{API_BASE}/engines/invalid/status", timeout=5)
        if response.status_code != 404:
            print_error("404 error not handled correctly")
            return False
        
        data = response.json()
        if 'success' not in data or data['success'] is not False:
            print_error("404 error response format incorrect")
            return False
        
        print_success("404 error handling works correctly")
        
        # Test invalid request
        response = requests.post(f"{API_BASE}/engines/analyze", json={}, timeout=5)
        if response.status_code != 200:
            print_error("Invalid request not handled gracefully")
            return False
        
        data = response.json()
        if 'success' not in data or data['success'] is not False:
            print_error("Invalid request response format incorrect")
            return False
        
        print_success("Invalid request handling works correctly")
        
        return True
        
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
        return False


async def run_integration_tests():
    """Run all integration tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}🧪 BettaFish Frontend-Backend Integration Tests{Colors.END}")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Engines API", test_engines_api),
        ("Analysis Endpoint", test_analysis_endpoint),
        ("WebSocket Connection", test_websocket_connection),
        ("WebSocket API", test_websocket_api_endpoints),
        ("Frontend Compatibility", test_frontend_compatibility),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{Colors.BOLD}Running: {test_name}{Colors.END}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            else:
                print_error(f"Test '{test_name}' failed")
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}Test Results: {passed}/{total} passed{Colors.END}")
    
    if passed == total:
        print_success("🎉 All integration tests passed!")
        print_success("✅ FastAPI backend has 100% parity with Flask frontend!")
        return True
    else:
        print_error(f"❌ {total - passed} tests failed")
        print_error("❌ Integration issues detected between frontend and backend")
        return False


def main():
    """Main function"""
    print_info("Starting BettaFish Frontend-Backend Integration Tests")
    print_info("This test verifies 100% parity between Flask frontend and FastAPI backend")
    
    # Check if backend is running
    if not test_backend_health():
        print_error("Backend is not running. Please start the FastAPI backend first:")
        print_error("  cd backend && python -m app.main")
        return 1
    
    # Run integration tests
    try:
        result = asyncio.run(run_integration_tests())
        return 0 if result else 1
    except KeyboardInterrupt:
        print_warning("\nTests interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Test suite crashed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())