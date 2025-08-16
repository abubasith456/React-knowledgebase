#!/usr/bin/env python3
"""
Simple API test script to validate the Knowledge Base Service backend
Run this to test core functionality without Docker
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from fastapi.testclient import TestClient
    from main import app
    import pytest
    
    # Create test client
    client = TestClient(app)
    
    def test_health_check():
        """Test health endpoint"""
        response = client.get("/health")
        print(f"✓ Health check: {response.status_code}")
        return response.status_code == 200
    
    def test_create_project():
        """Test project creation"""
        headers = {"x-api-key": "dev-api-key"}
        project_data = {
            "name": "Test Project",
            "description": "A test project for validation"
        }
        
        response = client.post("/api/v1/projects", json=project_data, headers=headers)
        print(f"✓ Create project: {response.status_code}")
        
        if response.status_code == 200:
            project = response.json()
            print(f"  Project ID: {project['id']}")
            print(f"  Project Name: {project['name']}")
            return project['id']
        return None
    
    def test_list_projects():
        """Test project listing"""
        headers = {"x-api-key": "dev-api-key"}
        response = client.get("/api/v1/projects", headers=headers)
        print(f"✓ List projects: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"  Found {len(projects)} projects")
            return len(projects)
        return 0
    
    def test_upload_small_document(project_id):
        """Test uploading a small document (<7K tokens)"""
        if not project_id:
            return False
            
        # Create a small test document
        test_content = "This is a small test document. " * 50  # ~250 tokens
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            headers = {"x-api-key": "dev-api-key"}
            
            with open(temp_file, 'rb') as f:
                files = {"files": ("test_small.txt", f, "text/plain")}
                response = client.post(
                    f"/api/v1/projects/{project_id}/upload", 
                    files=files, 
                    headers={"x-api-key": "dev-api-key"}
                )
            
            print(f"✓ Upload small document: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get('job_id')
                print(f"  Job ID: {job_id}")
                return job_id
                
        finally:
            os.unlink(temp_file)
        
        return None
    
    def test_job_status(job_id):
        """Test job status checking"""
        if not job_id:
            return False
            
        headers = {"x-api-key": "dev-api-key"}
        response = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
        print(f"✓ Job status check: {response.status_code}")
        
        if response.status_code == 200:
            job = response.json()
            print(f"  Status: {job['status']}")
            print(f"  Progress: {job['progress']}")
            return True
        
        return False
    
    def test_authentication():
        """Test API key authentication"""
        # Test without API key
        response = client.get("/api/v1/projects")
        print(f"✓ No API key (should fail): {response.status_code}")
        
        # Test with wrong API key
        headers = {"x-api-key": "wrong-key"}
        response = client.get("/api/v1/projects", headers=headers)
        print(f"✓ Wrong API key (should fail): {response.status_code}")
        
        # Test with correct API key
        headers = {"x-api-key": "dev-api-key"}
        response = client.get("/api/v1/projects", headers=headers)
        print(f"✓ Correct API key: {response.status_code}")
        
        return response.status_code == 200
    
    def run_tests():
        """Run all tests"""
        print("🧪 Testing Knowledge Base Service API\n")
        
        results = []
        
        # Test 1: Health check
        results.append(test_health_check())
        
        # Test 2: Authentication
        results.append(test_authentication())
        
        # Test 3: Create project
        project_id = test_create_project()
        results.append(project_id is not None)
        
        # Test 4: List projects
        project_count = test_list_projects()
        results.append(project_count > 0)
        
        # Test 5: Upload document
        job_id = test_upload_small_document(project_id)
        results.append(job_id is not None)
        
        # Test 6: Job status
        results.append(test_job_status(job_id))
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print(f"\n📊 Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All tests passed! The API is working correctly.")
        else:
            print("❌ Some tests failed. Check the logs above.")
        
        return passed == total
    
    if __name__ == "__main__":
        success = run_tests()
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("This test requires the backend dependencies to be installed.")
    print("In a real environment, you would run:")
    print("  cd backend && pip install -r requirements.txt")
    print("  python test_api.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed with error: {e}")
    sys.exit(1)