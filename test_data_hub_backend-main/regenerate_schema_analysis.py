#!/usr/bin/env python3
"""
Utility script to regenerate schema analysis for existing runs
This script will integrate business rules and test scenarios from the library generator
"""

import os
import sys
import json
import shutil

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schema_analyzer_agent import SchemaAnalyzerAgent

def regenerate_schema_analysis(run_id: str):
    """Regenerate schema analysis for a specific run to include business logic."""
    print(f"🔄 Regenerating schema analysis for run {run_id}")
    
    try:
        # Create a schema analyzer agent
        agent = SchemaAnalyzerAgent(api_key="dummy_key", run_id=run_id, mode="full")
        
        # Check if the run directory exists
        if not os.path.exists(agent.run_dir):
            print(f"❌ Run directory not found: {agent.run_dir}")
            return False
        
        # Check if business logic library exists
        library_dir = os.path.join(agent.run_dir, "business_logic_library")
        if not os.path.exists(library_dir):
            print(f"❌ Business logic library not found: {library_dir}")
            return False
        
        print(f"✅ Found business logic library: {library_dir}")
        
        # Check for existing business rules and test scenarios
        business_rules_file = os.path.join(library_dir, "business_rules.csv")
        test_scenarios_file = os.path.join(library_dir, "test_scenarios.csv")
        
        if os.path.exists(business_rules_file):
            print(f"📋 Found business rules: {business_rules_file}")
        else:
            print(f"⚠️  No business rules file found")
        
        if os.path.exists(test_scenarios_file):
            print(f"📋 Found test scenarios: {test_scenarios_file}")
        else:
            print(f"⚠️  No test scenarios file found")
        
        # Backup existing schema analysis
        schema_file = os.path.join(agent.schema_dir, "schema_analysis_results.json")
        if os.path.exists(schema_file):
            backup_file = schema_file.replace(".json", "_backup.json")
            shutil.copy2(schema_file, backup_file)
            print(f"💾 Backed up existing schema analysis to: {backup_file}")
        
        # Run the analysis with integration
        print("\n🚀 Running schema analysis with business logic integration...")
        result = agent.run_analysis_with_library_integration()
        
        if "error" in result:
            print(f"❌ Schema analysis failed: {result['error']}")
            return False
        
        print("✅ Schema analysis completed successfully!")
        
        # Verify the new schema file contains business logic
        if os.path.exists(schema_file):
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            
            total_rules = 0
            total_scenarios = 0
            
            if "tables" in schema_data:
                for table in schema_data["tables"]:
                    if "business_rules" in table:
                        total_rules += len(table["business_rules"])
                    if "test_scenarios" in table:
                        total_scenarios += len(table["test_scenarios"])
            
            print(f"📊 Final schema analysis contains:")
            print(f"   - {total_rules} business rules")
            print(f"   - {total_scenarios} test scenarios")
            
            if total_rules > 0 and total_scenarios > 0:
                print("✅ Business logic successfully integrated!")
                return True
            else:
                print("⚠️  No business logic found in final schema")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error regenerating schema analysis: {str(e)}")
        return False

def main():
    """Main function to regenerate schema analysis."""
    if len(sys.argv) != 2:
        print("Usage: python regenerate_schema_analysis.py <run_id>")
        print("Example: python regenerate_schema_analysis.py 22")
        sys.exit(1)
    
    run_id = sys.argv[1]
    
    print("🔄 Schema Analysis Regeneration Utility")
    print("=" * 50)
    print(f"Target Run ID: {run_id}")
    print()
    
    success = regenerate_schema_analysis(run_id)
    
    if success:
        print(f"\n🎉 Successfully regenerated schema analysis for run {run_id}")
        print("The schema_analysis_results.json file now includes business rules and test scenarios.")
    else:
        print(f"\n❌ Failed to regenerate schema analysis for run {run_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()
