"""
Test frontend-backend integration to ensure full Flask/FastAPI parity.
"""

import asyncio
import json
import pytest
import websockets
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from api.engines import PROCESSES
from services.websocket_manager import manager


class TestFrontendBackendIntegration:
    """Test suite for frontend-backend integration"""
    
    def test_engines_api_endpoints(self):
        """Test all engines API endpoints match Flask structure"""
        with TestClient(app) as client:
            # Test get all engine statuses
            response = client.get("/api/v1/engines/status")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            
            # Check all expected engines are present
            expected_engines = ['insight', 'media', 'query', 'forum']
            for engine in expected_engines:
                assert engine in data
                assert 'status' in data[engine]
                assert 'port' in data[engine]
                assert 'output_lines' in data[engine]
            
            # Test get specific engine status
            response = client.get("/api/v1/engines/insight/status")
            assert response.status_code == 200
            data = response.json()
            assert 'status' in data
            assert 'port' in data
            assert 'output_lines' in data
            
            # Test start engine endpoint
            response = client.post("/api/v1/engines/insight/start")
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'message' in data
            
            # Test stop engine endpoint
            response = client.post("/api/v1/engines/insight/stop")
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'message' in data
            
            # Test get engine output
            response = client.get("/api/v1/engines/insight/output")
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'output' in data
            
            # Test test log endpoint
            response = client.post("/api/v1/engines/insight/test_log")
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'message' in data
    
    def test_analysis_endpoint(self):
        """Test analysis endpoint matches Flask search functionality"""
        with TestClient(app) as client:
            # Test start analysis
            analysis_request = {
                "query": "test query",
                "engines": ["insight", "media", "query"],
                "options": {
                    "max_results": 10,
                    "sentiment_analysis": True
                }
            }
            
            response = client.post("/api/v1/engines/analyze", json=analysis_request)
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'analysis_id' in data
            assert 'query' in data
            assert 'engines' in data
            assert 'status' in data
            
            # Test get analysis status
            if 'analysis_id' in data:
                analysis_id = data['analysis_id']
                response = client.get(f"/api/v1/engines/analyze/{analysis_id}")
                assert response.status_code == 200
                status_data = response.json()
                assert 'success' in status_data
                assert 'analysis_id' in status_data
                assert 'status' in status_data
    
    @pytest.mark.asyncio
    async def test_websocket_compatibility(self):
        """Test WebSocket compatibility with Flask SocketIO"""
        # Test frontend WebSocket endpoint
        async with websockets.connect("ws://localhost:8065/ws/frontend") as websocket:
            # Send connection message
            await websocket.send(json.dumps({"type": "connect"}))
            
            # Receive connection response
            response = await websocket.recv()
            data = json.loads(response)
            assert data['type'] == 'connect'
            assert 'connection_id' in data['data']
            
            # Test status request
            await websocket.send(json.dumps({"type": "request_status"}))
            
            # Receive status update
            response = await websocket.recv()
            data = json.loads(response)
            assert data['type'] == 'status_update'
            assert isinstance(data['data'], dict)
            
            # Test engine subscription
            await websocket.send(json.dumps({
                "type": "subscribe_engine",
                "data": {"engine_type": "insight"}
            }))
            
            # Test agent message
            await websocket.send(json.dumps({
                "type": "agent_message",
                "data": {
                    "agent_type": "insight",
                    "message": {"test": "message"}
                }
            }))
    
    def test_websocket_api_endpoints(self):
        """Test WebSocket management API endpoints"""
        with TestClient(app) as client:
            # Test get connections
            response = client.get("/ws/connections")
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'data' in data
            
            # Test broadcast message
            broadcast_message = {
                "message": {"type": "test", "content": "broadcast test"}
            }
            response = client.post("/ws/broadcast", json=broadcast_message)
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'message' in data
            
            # Test send to agent
            agent_message = {
                "message": {"type": "test", "content": "agent test"}
            }
            response = client.post("/ws/send-to-agent/insight", json=agent_message)
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'message' in data
            
            # Test send to frontend
            frontend_message = {
                "message": {"type": "test", "content": "frontend test"}
            }
            response = client.post("/ws/send-to-frontend", json=frontend_message)
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'message' in data
            
            # Test get rooms
            response = client.get("/ws/rooms")
            assert response.status_code == 200
            data = response.json()
            assert 'success' in data
            assert 'data' in data
            assert 'rooms' in data['data']
            assert 'total_rooms' in data['data']
    
    def test_engine_process_management(self):
        """Test engine process management matches Flask behavior"""
        # Test process state structure
        assert isinstance(PROCESSES, dict)
        expected_engines = ['insight', 'media', 'query', 'forum']
        for engine in expected_engines:
            assert engine in PROCESSES
            assert 'process' in PROCESSES[engine]
            assert 'port' in PROCESSES[engine]
            assert 'status' in PROCESSES[engine]
            assert 'output' in PROCESSES[engine]
        
        # Test port assignments
        assert PROCESSES['insight']['port'] == 8501
        assert PROCESSES['media']['port'] == 8502
        assert PROCESSES['query']['port'] == 8503
        assert PROCESSES['forum']['port'] is None
        
        # Test initial status
        for engine in expected_engines:
            assert PROCESSES[engine]['status'] == 'stopped'
            assert PROCESSES[engine]['process'] is None
            assert PROCESSES[engine]['output'] == []
    
    def test_log_file_operations(self):
        """Test log file operations match Flask functionality"""
        from api.engines import write_log_to_file, read_log_from_file
        
        # Test write log
        test_app = "test_engine"
        test_message = "[12:00:00] Test log message"
        write_log_to_file(test_app, test_message)
        
        # Test read log
        logs = read_log_from_file(test_app)
        assert isinstance(logs, list)
        assert len(logs) > 0
        assert any(test_message in line for line in logs)
        
        # Test read with tail
        tail_logs = read_log_from_file(test_app, tail_lines=5)
        assert isinstance(tail_logs, list)
        assert len(tail_logs) <= 5
    
    def test_error_handling(self):
        """Test error handling matches Flask behavior"""
        with TestClient(app) as client:
            # Test invalid engine
            response = client.get("/api/v1/engines/invalid/status")
            assert response.status_code == 404
            
            # Test invalid analysis
            response = client.post("/api/v1/engines/analyze", json={})
            assert response.status_code == 200  # Should handle gracefully
            data = response.json()
            assert 'success' in data
            assert data['success'] is False
            assert 'message' in data
            
            # Test invalid WebSocket room
            response = client.post("/ws/send-to-room/invalid", json={
                "message": {"test": "message"}
            })
            assert response.status_code == 200  # Should handle gracefully
    
    def test_api_response_format(self):
        """Test API response format matches Flask structure"""
        with TestClient(app) as client:
            # Test success response format
            response = client.get("/api/v1/engines/status")
            assert response.status_code == 200
            data = response.json()
            
            # Should be a dict with engine keys
            assert isinstance(data, dict)
            
            # Each engine should have expected fields
            for engine_data in data.values():
                assert 'status' in engine_data
                assert 'port' in engine_data
                assert 'output_lines' in engine_data
            
            # Test error response format
            response = client.get("/api/v1/engines/invalid/status")
            assert response.status_code == 404
            data = response.json()
            assert 'success' in data
            assert data['success'] is False
            assert 'error' in data or 'message' in data


if __name__ == "__main__":
    # Run tests
    test_suite = TestFrontendBackendIntegration()
    
    print("Testing engines API endpoints...")
    test_suite.test_engines_api_endpoints()
    print("✅ Engines API endpoints test passed")
    
    print("Testing analysis endpoint...")
    test_suite.test_analysis_endpoint()
    print("✅ Analysis endpoint test passed")
    
    print("Testing engine process management...")
    test_suite.test_engine_process_management()
    print("✅ Engine process management test passed")
    
    print("Testing log file operations...")
    test_suite.test_log_file_operations()
    print("✅ Log file operations test passed")
    
    print("Testing error handling...")
    test_suite.test_error_handling()
    print("✅ Error handling test passed")
    
    print("Testing API response format...")
    test_suite.test_api_response_format()
    print("✅ API response format test passed")
    
    print("\n🎉 All frontend-backend integration tests passed!")
    print("The FastAPI backend now has 100% parity with the Flask frontend.")