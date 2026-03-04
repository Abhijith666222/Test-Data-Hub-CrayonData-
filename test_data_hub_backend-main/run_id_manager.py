#!/usr/bin/env python3
"""
Run ID Manager

Manages simple serial number run IDs instead of complex timestamps.
"""

import os
import json
from datetime import datetime

class RunIDManager:
    def __init__(self, base_dir: str = "runs"):
        self.base_dir = base_dir
        self.run_counter_file = os.path.join(base_dir, "run_counter.json")
        self.ensure_counter_file()
    
    def ensure_counter_file(self):
        """Ensure the counter file exists."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)
        
        if not os.path.exists(self.run_counter_file):
            with open(self.run_counter_file, 'w') as f:
                json.dump({"next_run_id": 1}, f)
    
    def get_next_run_id(self) -> str:
        """Get the next available run ID."""
        with open(self.run_counter_file, 'r') as f:
            counter = json.load(f)
        
        run_id = str(counter["next_run_id"])
        
        # Increment counter
        counter["next_run_id"] += 1
        
        with open(self.run_counter_file, 'w') as f:
            json.dump(counter, f)
        
        return run_id
    
    def list_existing_runs(self) -> list:
        """List all existing run IDs."""
        if not os.path.exists(self.base_dir):
            return []
        
        runs = []
        for item in os.listdir(self.base_dir):
            if item.isdigit() and os.path.isdir(os.path.join(self.base_dir, item)):
                runs.append(item)
        
        return sorted(runs, key=int)
    
    def run_exists(self, run_id: str) -> bool:
        """Check if a run ID exists."""
        run_path = os.path.join(self.base_dir, run_id)
        return os.path.exists(run_path) and os.path.isdir(run_path)
    
    def get_run_info(self, run_id: str) -> dict:
        """Get information about a specific run."""
        run_path = os.path.join(self.base_dir, run_id)
        if not os.path.exists(run_path):
            return None
        
        info = {
            "run_id": run_id,
            "path": run_path,
            "exists": True,
            "has_schema": False,
            "has_synthetic_data": False,
            "has_validation": False,
            "has_input_data": False
        }
        
        # Check what files exist
        schema_dir = os.path.join(run_path, "schema")
        if os.path.exists(schema_dir):
            info["has_schema"] = os.path.exists(os.path.join(schema_dir, "schema_analysis_results.json"))
        
        synthetic_data_dir = os.path.join(run_path, "synthetic_data")
        if os.path.exists(synthetic_data_dir):
            data_dir = os.path.join(synthetic_data_dir, "data")
            if os.path.exists(data_dir):
                csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                info["has_synthetic_data"] = len(csv_files) > 0
        
        validation_dir = os.path.join(run_path, "validation")
        if os.path.exists(validation_dir):
            reports_dir = os.path.join(validation_dir, "reports")
            if os.path.exists(reports_dir):
                info["has_validation"] = os.path.exists(os.path.join(reports_dir, "validation_report.json"))
        
        input_data_dir = os.path.join(run_path, "input_data")
        if os.path.exists(input_data_dir):
            # Check for input data in the new nested structure
            data_dir = os.path.join(input_data_dir, "data")
            if os.path.exists(data_dir):
                csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                info["has_input_data"] = len(csv_files) > 0
            else:
                # Fallback to old structure
                csv_files = [f for f in os.listdir(input_data_dir) if f.endswith('.csv')]
                info["has_input_data"] = len(csv_files) > 0
        
        return info

def get_run_id_manager():
    """Get a RunIDManager instance."""
    return RunIDManager()

def generate_run_id() -> str:
    """Generate a new run ID."""
    manager = get_run_id_manager()
    return manager.get_next_run_id()

def list_runs() -> list:
    """List all existing runs."""
    manager = get_run_id_manager()
    return manager.list_existing_runs()

def run_exists(run_id: str) -> bool:
    """Check if a run exists."""
    manager = get_run_id_manager()
    return manager.run_exists(run_id)

def get_run_info(run_id: str) -> dict:
    """Get information about a run."""
    manager = get_run_id_manager()
    return manager.get_run_info(run_id) 