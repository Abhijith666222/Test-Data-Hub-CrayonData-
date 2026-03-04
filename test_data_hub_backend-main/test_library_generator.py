#!/usr/bin/env python3
"""
Test script for the Library Generator Agent
This script tests the deduplication and formatting fixes
"""

import os
import sys
import json
import tempfile
import shutil

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from business_logic_library.library_generator_agent import LibraryGeneratorAgent

def test_deduplication():
    """Test the deduplication functionality."""
    print("🧪 Testing deduplication functionality...")
    
    # Create test data with duplicates
    test_business_rules = [
        {
            "table_name": "credit_card_products",
            "rule_name": "Product Active Status",
            "rule_type": "business_logic",
            "description": "Product must be active for issuing new cards",
            "validation_logic": "active_flag = 'Y'",
            "error_message": "Inactive product used for issuing new cards",
            "severity": "HIGH",
            "is_active": 1
        },
        {
            "table_name": "credit_card_products",
            "rule_name": "Product Active Status",
            "rule_type": "business_logic",
            "description": "Product must be active for issuing new cards",
            "validation_logic": "active_flag = 'Y'",
            "error_message": "Inactive product used for issuing new cards",
            "severity": "HIGH",
            "is_active": 1
        }
    ]
    
    test_test_scenarios = [
        {
            "table_name": "credit_card_products",
            "scenario_name": "Test Inactive Product Issuance",
            "scenario_type": "negative",
            "description": "Test scenario where an inactive product is used for issuing a card",
            "test_conditions": "active_flag = 'N'",
            "expected_behavior": "Product issuance should be rejected",
            "data_requirements": "Product with active_flag = 'N'",
            "priority": "HIGH",
            "is_active": 1
        },
        {
            "table_name": "credit_card_products",
            "scenario_name": "Test Inactive Product Issuance",
            "scenario_type": "negative",
            "description": "Test scenario where an inactive product is used for issuing a card",
            "test_conditions": "active_flag = 'N'",
            "expected_behavior": "Product issuance should be rejected",
            "data_requirements": "Product with active_flag = 'N'",
            "priority": "HIGH",
            "is_active": 1
        }
    ]
    
    # Create a temporary agent instance
    temp_run_id = "test_dedup_001"
    agent = LibraryGeneratorAgent(run_id=temp_run_id, mode="data_analysis")
    
    # Test deduplication
    unique_rules, unique_scenarios = agent.deduplicate_business_logic(test_business_rules, test_test_scenarios)
    
    print(f"Original business rules: {len(test_business_rules)}")
    print(f"Original test scenarios: {len(test_test_scenarios)}")
    print(f"Unique business rules: {len(unique_rules)}")
    print(f"Unique test scenarios: {len(unique_scenarios)}")
    
    # Verify deduplication worked
    assert len(unique_rules) == 1, f"Expected 1 unique rule, got {len(unique_rules)}"
    assert len(unique_scenarios) == 1, f"Expected 1 unique scenario, got {len(unique_scenarios)}"
    
    print("✅ Deduplication test passed!")
    return True

def test_relationship_validation():
    """Test the cross-table relationship validation."""
    print("\n🧪 Testing cross-table relationship validation...")
    
    # Create test relationships
    test_relationships = [
        {
            "from_table": "customer_info",
            "to_table": "credit_card_accounts",
            "relationship_type": "one_to_many"
        }
    ]
    
    # Create a temporary agent instance
    temp_run_id = "test_rel_001"
    agent = LibraryGeneratorAgent(run_id=temp_run_id, mode="data_analysis")
    
    # Test validation
    valid_relationships = agent.validate_cross_table_relationships(test_relationships)
    
    print(f"Input relationships: {len(test_relationships)}")
    print(f"Validated relationships: {len(valid_relationships)}")
    
    # Verify validation worked
    assert len(valid_relationships) == 3, f"Expected 3 relationships, got {len(valid_relationships)}"
    
    # Check that all required fields are present
    for rel in valid_relationships:
        required_fields = ["from_table", "to_table", "relationship_type", "description", "foreign_key"]
        for field in required_fields:
            assert field in rel, f"Missing required field: {field}"
    
    print("✅ Relationship validation test passed!")
    return True

def test_schema_analysis_creation():
    """Test the schema analysis creation with proper formatting."""
    print("\n🧪 Testing schema analysis creation...")
    
    # Create test input data
    import pandas as pd
    test_input_data = {
        "credit_card_products": pd.DataFrame({
            "product_code": ["PROD001", "PROD002"],
            "active_flag": ["Y", "N"]
        })
    }
    
    # Create test business rules and scenarios
    test_business_rules = [
        {
            "table_name": "credit_card_products",
            "rule_name": "Product Active Status",
            "rule_type": "business_logic",
            "description": "Product must be active for issuing new cards",
            "validation_logic": "active_flag = 'Y'",
            "error_message": "Inactive product used for issuing new cards",
            "severity": "HIGH",
            "is_active": 1
        }
    ]
    
    test_test_scenarios = [
        {
            "table_name": "credit_card_products",
            "scenario_name": "Test Inactive Product Issuance",
            "scenario_type": "negative",
            "description": "Test scenario where an inactive product is used for issuing a card",
            "test_conditions": "active_flag = 'N'",
            "expected_behavior": "Product issuance should be rejected",
            "data_requirements": "Product with active_flag = 'N'",
            "priority": "HIGH",
            "is_active": 1
        }
    ]
    
    # Create a temporary agent instance
    temp_run_id = "test_schema_001"
    agent = LibraryGeneratorAgent(run_id=temp_run_id, mode="data_analysis")
    
    # Test schema analysis creation
    agent.create_basic_schema_analysis(test_input_data, test_business_rules, test_test_scenarios)
    
    # Check if the file was created
    schema_file = os.path.join(agent.schema_dir, "schema_analysis_results.json")
    assert os.path.exists(schema_file), f"Schema analysis file not created: {schema_file}"
    
    # Load and validate the created file
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    # Verify structure
    assert "tables" in schema_data, "Missing 'tables' in schema analysis"
    assert "cross_table_relationships" in schema_data, "Missing 'cross_table_relationships' in schema analysis"
    assert len(schema_data["tables"]) == 1, f"Expected 1 table, got {len(schema_data['tables'])}"
    assert len(schema_data["cross_table_relationships"]) == 3, f"Expected 3 relationships, got {len(schema_data['cross_table_relationships'])}"
    
    # Verify table structure
    table = schema_data["tables"][0]
    assert "business_rules" in table, "Missing 'business_rules' in table"
    assert "test_scenarios" in table, "Missing 'test_scenarios' in table"
    assert len(table["business_rules"]) == 1, f"Expected 1 business rule, got {len(table['business_rules'])}"
    assert len(table["test_scenarios"]) == 1, f"Expected 1 test scenario, got {len(table['test_scenarios'])}"
    
    print("✅ Schema analysis creation test passed!")
    
    # Clean up
    if os.path.exists(agent.run_dir):
        shutil.rmtree(agent.run_dir)
    
    return True

def main():
    """Run all tests."""
    print("🚀 Library Generator Agent Test Suite")
    print("=" * 50)
    
    try:
        test_deduplication()
        test_relationship_validation()
        test_schema_analysis_creation()
        
        print("\n🎉 All tests passed successfully!")
        print("The library generator agent is now properly formatted and deduplicated.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
