#!/usr/bin/env python3
"""
Test script for the Schema Analyzer Agent fixes
This script tests the deduplication and minimum count functionality
"""

import os
import sys
import json
import tempfile
import shutil

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schema_analyzer_agent import SchemaAnalyzerAgent

def test_deduplication():
    """Test the deduplication functionality."""
    print("🧪 Testing schema analyzer deduplication...")
    
    # Create test data with duplicates
    test_analysis = {
        "tables": [
            {
                "table_name": "credit_card_accounts",
                "business_rules": [
                    {
                        "rule_name": "Credit Limit Check",
                        "description": "Credit limit must be positive",
                        "validation_logic": "credit_limit > 0",
                        "error_message": "Credit limit must be positive"
                    },
                    {
                        "rule_name": "Credit Limit Check",
                        "description": "Credit limit must be positive",
                        "validation_logic": "credit_limit > 0",
                        "error_message": "Credit limit must be positive"
                    }
                ],
                "test_scenarios": [
                    {
                        "scenario_name": "High Value Transaction",
                        "description": "Test high value transaction",
                        "test_type": "positive",
                        "business_logic": "amount > 10000",
                        "expected_behavior": "Transaction approved"
                    },
                    {
                        "scenario_name": "High Value Transaction",
                        "description": "Test high value transaction",
                        "test_type": "positive",
                        "business_logic": "amount > 10000",
                        "expected_behavior": "Transaction approved"
                    }
                ]
            }
        ]
    }
    
    # Create a temporary agent instance
    temp_run_id = "test_schema_001"
    agent = SchemaAnalyzerAgent(run_id=temp_run_id, mode="full")
    
    # Test deduplication
    processed_analysis = agent.post_process_analysis(test_analysis)
    
    # Check results
    table = processed_analysis["tables"][0]
    business_rules = table["business_rules"]
    test_scenarios = table["test_scenarios"]
    
    print(f"Original business rules: 2")
    print(f"Original test scenarios: 2")
    print(f"Final business rules: {len(business_rules)}")
    print(f"Final test scenarios: {len(test_scenarios)}")
    
    # Verify deduplication worked
    assert len(business_rules) == 1, f"Expected 1 unique business rule, got {len(business_rules)}"
    assert len(test_scenarios) == 1, f"Expected 1 unique test scenario, got {len(test_scenarios)}"
    
    print("✅ Schema analyzer deduplication test passed!")
    return True

def test_minimum_count():
    """Test the minimum count functionality."""
    print("\n🧪 Testing schema analyzer minimum count...")
    
    # Create test data with insufficient items
    test_analysis = {
        "tables": [
            {
                "table_name": "credit_card_accounts",
                "business_rules": [
                    {
                        "rule_name": "Credit Limit Check",
                        "description": "Credit limit must be positive",
                        "validation_logic": "credit_limit > 0",
                        "error_message": "Credit limit must be positive"
                    }
                ],
                "test_scenarios": []
            }
        ]
    }
    
    # Create a temporary agent instance
    temp_run_id = "test_schema_002"
    agent = SchemaAnalyzerAgent(run_id=temp_run_id, mode="full")
    
    # Test minimum count
    processed_analysis = agent.post_process_analysis(test_analysis)
    
    # Check results
    table = processed_analysis["tables"][0]
    business_rules = table["business_rules"]
    test_scenarios = table["test_scenarios"]
    
    print(f"Original business rules: 1")
    print(f"Original test scenarios: 0")
    print(f"Final business rules: {len(business_rules)}")
    print(f"Final test scenarios: {len(test_scenarios)}")
    
    # Verify minimum count was achieved
    assert len(business_rules) >= 3, f"Expected at least 3 business rules, got {len(business_rules)}"
    assert len(test_scenarios) >= 3, f"Expected at least 3 test scenarios, got {len(test_scenarios)}"
    
    print("✅ Schema analyzer minimum count test passed!")
    return True

def main():
    """Run all tests."""
    print("🚀 Schema Analyzer Agent Fixes Test Suite")
    print("=" * 50)
    
    try:
        test_deduplication()
        test_minimum_count()
        
        print("\n🎉 All tests passed successfully!")
        print("The schema analyzer agent is now properly deduplicated and ensures minimum counts.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
