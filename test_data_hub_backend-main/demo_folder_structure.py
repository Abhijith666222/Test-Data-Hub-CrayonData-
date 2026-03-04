#!/usr/bin/env python3
"""
Demo Script: Folder Structure

This script demonstrates the new folder structure and creates a sample run
to show how the system organizes outputs.
"""

import os
import shutil
from datetime import datetime

def create_demo_structure():
    """Create a demo folder structure to show the new organization."""
    
    # Generate a demo run ID
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define the folder structure
    base_dir = "runs"
    run_dir = os.path.join(base_dir, run_id)
    
    # Create the directory structure
    directories = [
        run_dir,
        os.path.join(run_dir, "input_data"),
        os.path.join(run_dir, "schema"),
        os.path.join(run_dir, "synthetic_data"),
        os.path.join(run_dir, "validation")
    ]
    
    print(f"🚀 Creating Demo Folder Structure")
    print(f"📁 Run ID: {run_id}")
    print(f"📂 Base Directory: {base_dir}")
    print("="*60)
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # Create sample files to demonstrate the structure
    sample_files = {
        "schema/schema_analysis_results.json": '{"tables": [], "cross_table_relationships": []}',
        "synthetic_data/customer_info.csv": "customer_id,name,email\nCUST001,John Doe,john@example.com",
        "synthetic_data/credit_card_accounts.csv": "account_id,customer_id,balance\nACC001,CUST001,1000.00",
        "validation/validation_report.json": '{"overall_status": "PASS", "tables": {}}',
        "validation/validation_summary.txt": "Validation completed successfully\nAll business rules passed"
    }
    
    print("\n📄 Creating Sample Files:")
    for file_path, content in sample_files.items():
        full_path = os.path.join(run_dir, file_path)
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✅ Created: {file_path}")
    
    # Display the final structure
    print(f"\n📊 Final Folder Structure:")
    print(f"runs/")
    print(f"└── {run_id}/")
    print(f"    ├── input_data/")
    print(f"    ├── schema/")
    print(f"    │   └── schema_analysis_results.json")
    print(f"    ├── synthetic_data/")
    print(f"    │   ├── customer_info.csv")
    print(f"    │   └── credit_card_accounts.csv")
    print(f"    └── validation/")
    print(f"        ├── validation_report.json")
    print(f"        └── validation_summary.txt")
    
    print(f"\n🎉 Demo structure created successfully!")
    print(f"📁 Location: {run_dir}")
    
    return run_dir

def show_existing_runs():
    """Show existing runs in the runs directory."""
    base_dir = "runs"
    
    if not os.path.exists(base_dir):
        print("❌ No runs directory found.")
        return
    
    runs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    if not runs:
        print("📁 No existing runs found.")
        return
    
    print(f"\n📊 Existing Runs:")
    print("="*40)
    
    for run in sorted(runs, reverse=True):
        run_path = os.path.join(base_dir, run)
        
        # Count files in each subdirectory
        schema_files = len([f for f in os.listdir(os.path.join(run_path, "schema")) if os.path.isfile(os.path.join(run_path, "schema", f))]) if os.path.exists(os.path.join(run_path, "schema")) else 0
        data_files = len([f for f in os.listdir(os.path.join(run_path, "synthetic_data")) if f.endswith('.csv')]) if os.path.exists(os.path.join(run_path, "synthetic_data")) else 0
        validation_files = len([f for f in os.listdir(os.path.join(run_path, "validation")) if os.path.isfile(os.path.join(run_path, "validation", f))]) if os.path.exists(os.path.join(run_path, "validation")) else 0
        
        print(f"📁 {run}")
        print(f"   📋 Schema: {schema_files} files")
        print(f"   🔧 Data: {data_files} CSV files")
        print(f"   🔍 Validation: {validation_files} files")
        print()

def main():
    """Main function to run the demo."""
    print("🎯 Test Data Environment - Folder Structure Demo")
    print("="*60)
    
    # Show existing runs first
    show_existing_runs()
    
    # Create demo structure
    demo_dir = create_demo_structure()
    
    print(f"\n💡 Key Benefits of This Structure:")
    print("   ✅ Each run is isolated in its own folder")
    print("   ✅ Easy to compare different runs")
    print("   ✅ Organized by function (schema, data, validation)")
    print("   ✅ Unique timestamps prevent conflicts")
    print("   ✅ Clean separation of concerns")
    
    print(f"\n🔧 Next Steps:")
    print(f"   1. Run: python run_complete_pipeline.py")
    print(f"   2. Check the generated folder structure")
    print(f"   3. Compare outputs between different runs")
    
    print(f"\n📁 Demo run created at: {demo_dir}")

if __name__ == "__main__":
    main() 