#!/usr/bin/env python3
"""
API Client for Test Data Environment Backend
Comprehensive client to test all endpoints and demonstrate functionality
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class TestDataEnvironmentClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def health_check(self) -> Dict[str, Any]:
        """Check if the server is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def get_runs(self) -> List[Dict[str, Any]]:
        """Get all available runs."""
        try:
            response = self.session.get(f"{self.base_url}/runs")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get runs: {e}")
            return []
    
    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get specific run information."""
        try:
            response = self.session.get(f"{self.base_url}/runs/{run_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get run {run_id}: {e}")
            return {}
    
    def run_schema_analysis(self, run_id: str = None, mode: str = "full") -> Dict[str, Any]:
        """Run schema analysis."""
        try:
            payload = {
                "run_id": run_id,
                "mode": mode
            }
            response = self.session.post(f"{self.base_url}/schema-analysis", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to start schema analysis: {e}")
            return {}
    
    def generate_synthetic_data(self, run_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate synthetic data."""
        try:
            payload = {
                "run_id": run_id,
                "config": config or {}
            }
            response = self.session.post(f"{self.base_url}/generate-data", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to start data generation: {e}")
            return {}
    
    def get_test_scenarios(self, run_id: str) -> Dict[str, Any]:
        """Get available test scenarios."""
        try:
            response = self.session.get(f"{self.base_url}/runs/{run_id}/test-scenarios")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get test scenarios: {e}")
            return {}
    
    def generate_test_scenarios(self, run_id: str, selected_scenarios: List[int], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate test scenario data."""
        try:
            payload = {
                "run_id": run_id,
                "selected_scenarios": selected_scenarios,
                "config": config or {}
            }
            response = self.session.post(f"{self.base_url}/generate-test-scenarios", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to start test scenario generation: {e}")
            return {}
    
    def run_validation(self, run_id: str) -> Dict[str, Any]:
        """Run validation."""
        try:
            payload = {"run_id": run_id}
            response = self.session.post(f"{self.base_url}/validate", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to start validation: {e}")
            return {}
    
    def get_run_files(self, run_id: str) -> Dict[str, Any]:
        """Get files generated for a run."""
        try:
            response = self.session.get(f"{self.base_url}/runs/{run_id}/files")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get run files: {e}")
            return {}
    
    def download_file(self, run_id: str, file_type: str, filename: str) -> Dict[str, Any]:
        """Download a specific file."""
        try:
            response = self.session.get(f"{self.base_url}/runs/{run_id}/files/{file_type}/{filename}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to download file: {e}")
            return {}
    
    def run_complete_pipeline(self, run_id: str = None, mode: str = "full") -> Dict[str, Any]:
        """Run the complete pipeline."""
        try:
            payload = {
                "run_id": run_id,
                "mode": mode
            }
            response = self.session.post(f"{self.base_url}/pipeline/complete", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to start complete pipeline: {e}")
            return {}

def demo_workflow():
    """Demonstrate the complete workflow."""
    print("🚀 Test Data Environment API Client Demo")
    print("=" * 60)
    
    client = TestDataEnvironmentClient()
    
    # 1. Health check
    print("\n1️⃣ Health Check")
    health = client.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    
    if health.get('status') != 'healthy':
        print("❌ Server is not healthy. Please start the FastAPI server first.")
        return
    
    # 2. Get existing runs
    print("\n2️⃣ Existing Runs")
    runs = client.get_runs()
    print(f"   Found {len(runs)} existing runs")
    for run in runs:
        status = []
        if run.get('has_schema'): status.append("📋 Schema")
        if run.get('has_synthetic_data'): status.append("🔧 Data")
        if run.get('has_validation'): status.append("🔍 Validation")
        if run.get('has_input_data'): status.append("📥 Input")
        print(f"   Run {run['run_id']}: {' | '.join(status) if status else 'Empty'}")
    
    # 3. Start a new run with schema analysis
    print("\n3️⃣ Starting Schema Analysis")
    schema_result = client.run_schema_analysis(mode="full")
    if schema_result:
        run_id = schema_result.get('run_id')
        print(f"   ✅ Schema analysis started for run {run_id}")
        print(f"   Status: {schema_result.get('status')}")
        print(f"   Message: {schema_result.get('message')}")
        
        # Wait a bit for schema analysis to complete
        print("   ⏳ Waiting for schema analysis to complete...")
        time.sleep(10)
        
        # 4. Check run status
        print("\n4️⃣ Checking Run Status")
        run_info = client.get_run(run_id)
        if run_info:
            print(f"   Run {run_id} status:")
            print(f"   - Has schema: {run_info.get('has_schema')}")
            print(f"   - Has input data: {run_info.get('has_input_data')}")
            print(f"   - Has synthetic data: {run_info.get('has_synthetic_data')}")
            print(f"   - Has validation: {run_info.get('has_validation')}")
        
        # 5. Generate synthetic data
        print("\n5️⃣ Generating Synthetic Data")
        data_config = {
            "default_records": 100,
            "data_quality": "high",
            "include_edge_cases": True
        }
        data_result = client.generate_synthetic_data(run_id, data_config)
        if data_result:
            print(f"   ✅ Data generation started")
            print(f"   Status: {data_result.get('status')}")
            print(f"   Message: {data_result.get('message')}")
            
            # Wait for data generation
            print("   ⏳ Waiting for data generation to complete...")
            time.sleep(15)
        
        # 6. Get test scenarios
        print("\n6️⃣ Getting Test Scenarios")
        scenarios_result = client.get_test_scenarios(run_id)
        if scenarios_result and scenarios_result.get('scenarios'):
            scenarios = scenarios_result['scenarios']
            print(f"   Found {len(scenarios)} test scenarios")
            
            # Show first few scenarios
            for i, scenario in enumerate(scenarios[:3]):
                print(f"   {i+1}. [{scenario.get('table_name', 'N/A')}] {scenario.get('scenario_name', 'N/A')}")
                print(f"      Type: {scenario.get('scenario_type', 'N/A')}, Priority: {scenario.get('priority', 'N/A')}")
            
            # 7. Generate test scenario data
            print("\n7️⃣ Generating Test Scenario Data")
            selected_scenarios = [0, 1, 2]  # First 3 scenarios
            test_config = {
                "default_records": 10,
                "priority_multipliers": {
                    "CRITICAL": 2.0,
                    "HIGH": 1.5,
                    "MEDIUM": 1.0,
                    "LOW": 0.5
                }
            }
            test_result = client.generate_test_scenarios(run_id, selected_scenarios, test_config)
            if test_result:
                print(f"   ✅ Test scenario generation started")
                print(f"   Status: {test_result.get('status')}")
                print(f"   Message: {test_result.get('message')}")
                
                # Wait for test scenario generation
                print("   ⏳ Waiting for test scenario generation to complete...")
                time.sleep(10)
        
        # 8. Run validation
        print("\n8️⃣ Running Validation")
        validation_result = client.run_validation(run_id)
        if validation_result:
            print(f"   ✅ Validation started")
            print(f"   Status: {validation_result.get('status')}")
            print(f"   Message: {validation_result.get('message')}")
            
            # Wait for validation
            print("   ⏳ Waiting for validation to complete...")
            time.sleep(10)
        
        # 9. Get generated files
        print("\n9️⃣ Generated Files")
        files_result = client.get_run_files(run_id)
        if files_result and files_result.get('files'):
            files = files_result['files']
            for file_type, file_list in files.items():
                if file_list:
                    print(f"   {file_type}:")
                    for file_info in file_list[:3]:  # Show first 3 files
                        size_kb = file_info['size'] / 1024
                        print(f"     - {file_info['name']} ({size_kb:.1f} KB)")
        
        # 10. Download a sample file
        print("\n🔟 Downloading Sample File")
        if files_result and files_result.get('files', {}).get('schema'):
            sample_file = files_result['files']['schema'][0]['name']
            file_content = client.download_file(run_id, 'schema', sample_file)
            if file_content:
                print(f"   ✅ Downloaded {sample_file}")
                content = file_content.get('content', '')
                print(f"   Content length: {len(content)} characters")
                print(f"   Preview: {content[:200]}...")
    
    print("\n🎉 Demo completed!")
    print("=" * 60)
    print("💡 Tips:")
    print("   - Use the WebSocket client (websocket_client.py) to see real-time logs")
    print("   - Check the FastAPI docs at http://localhost:8000/docs")
    print("   - All generated files are stored in the runs/ directory")

def test_individual_endpoints():
    """Test individual endpoints."""
    print("🧪 Testing Individual Endpoints")
    print("=" * 60)
    
    client = TestDataEnvironmentClient()
    
    # Test health check
    print("\n🔍 Testing Health Check")
    health = client.health_check()
    print(f"Health: {health}")
    
    # Test getting runs
    print("\n📊 Testing Get Runs")
    runs = client.get_runs()
    print(f"Runs: {len(runs)} found")
    
    # Test complete pipeline
    print("\n🚀 Testing Complete Pipeline")
    pipeline_result = client.run_complete_pipeline(mode="full")
    print(f"Pipeline: {pipeline_result}")

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_individual_endpoints()
    else:
        demo_workflow()

if __name__ == "__main__":
    main() 