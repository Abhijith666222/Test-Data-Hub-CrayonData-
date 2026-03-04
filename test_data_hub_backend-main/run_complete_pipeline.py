#!/usr/bin/env python3
"""
Complete Pipeline Orchestrator

This script runs the complete test data generation pipeline with support for two user journeys:

Synthetic Data Generation: Schema-only input → Full pipeline (schema analysis + test scenarios + business logic → synthetic data → validation)
Functional Test Scenario Generation: Data + Schema input → Schema analysis only → Business logic generation → Test scenario generation → Validation

Each run creates a unique folder structure with all outputs organized.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import OPENAI_API_KEY
from schema_analyzer_agent import SchemaAnalyzerAgent
from synthetic_data_generator_agent import SyntheticDataGeneratorAgent
from validation_agent import ValidationAgent
from test_scenario_data_generator_agent import TestScenarioDataGeneratorAgent
from business_logic_library.library_generator_agent import LibraryGeneratorAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self, run_id: str = None, journey: str = "1"):
        """Initialize the pipeline orchestrator.
        
        Args:
            run_id: Unique run ID (auto-generated if None)
            journey: User journey - "1" (schema-only) or "2" (data + schema)
        """
        # Generate unique run ID if not provided
        if run_id is None:
            self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.run_id = run_id
        
        self.journey = journey
        
        # Define folder structure
        self.base_dir = "runs"
        self.run_dir = os.path.join(self.base_dir, self.run_id)
        
        print(f"\n🚀 Starting Pipeline Run: {self.run_id}")
        print(f"📁 Run Directory: {self.run_dir}")
        print(f"🎯 User Journey: {journey}")
        print("="*80)
    
    def run_journey_1(self) -> bool:
        """Run Synthetic Data Generation: Schema-only → Full Pipeline."""
        print("\n🎯 SYNTHETIC DATA GENERATION: Schema-only → Full Pipeline")
        print("="*60)
        
        # Step 1: Schema Analysis (with test scenarios and business logic)
        if not self.run_schema_analysis(mode="full"):
            print("❌ Pipeline failed at schema analysis step")
            return False
        
        # Step 2: Synthetic Data Generation
        if not self.run_synthetic_data_generation():
            print("❌ Pipeline failed at synthetic data generation step")
            return False
        
        # Step 3: Validation
        if not self.run_validation():
            print("❌ Pipeline failed at validation step")
            return False
        
        # Step 4: Test Scenario Generation (optional)
        if not self.run_test_scenario_generation():
            print("❌ Pipeline failed at test scenario generation step")
            return False
        
        return True
    
    def run_journey_2(self) -> bool:
        """Run Functional Test Scenario Generation: Data + Schema → Schema analysis → Business logic → Test scenarios → Validation."""
        print("\n🎯 FUNCTIONAL TEST SCENARIO GENERATION: Data + Schema → Business Logic → Test Scenarios → Validation")
        print("="*60)
        
        # Step 1: Schema Analysis (schema-only, no test scenarios or business logic)
        if not self.run_schema_analysis(mode="schema_only"):
            print("❌ Pipeline failed at schema analysis step")
            return False
        
        # Step 2: Business Logic Generation
        if not self.run_business_logic_generation():
            print("❌ Pipeline failed at business logic generation step")
            return False
        
        # Step 3: Test Scenario Generation
        if not self.run_test_scenario_generation():
            print("❌ Pipeline failed at test scenario generation step")
            return False
        
        # Step 4: Validation
        if not self.run_validation():
            print("❌ Pipeline failed at validation step")
            return False
        
        return True
    
    def run_schema_analysis(self, mode: str = "full") -> bool:
        """Run schema analysis step."""
        print(f"\n📋 STEP 1: SCHEMA ANALYSIS (Mode: {mode})")
        print("-" * 50)
        
        try:
            agent = SchemaAnalyzerAgent(OPENAI_API_KEY, self.run_id, mode=mode)
            results = agent.run_analysis()
            
            if "error" not in results:
                print("✅ Schema analysis completed successfully")
                return True
            else:
                print(f"❌ Schema analysis failed: {results['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error in schema analysis: {str(e)}")
            print(f"❌ Schema analysis failed: {str(e)}")
            return False
    
    def run_synthetic_data_generation(self) -> bool:
        """Run synthetic data generation step."""
        print("\n🔧 STEP 2: SYNTHETIC DATA GENERATION")
        print("-" * 50)
        
        try:
            agent = SyntheticDataGeneratorAgent(OPENAI_API_KEY, self.run_id)
            
            # Configuration for data generation
            config = {
                "volume_percentage": 0.05,  # Generate 5% of recommended volumes for testing
                "volume_overrides": {
                    "customer_info": 500,
                    "credit_card_accounts": 750,
                    "credit_card_products": 10,
                    "credit_card_transactions": 2500,
                    "imobile_user_session": 2500
                },
                "scenario_mix": {
                    "positive": 0.7,
                    "negative": 0.2,
                    "edge_case": 0.1
                },
                "output_format": "csv",
                "seed": 42
            }
            
            success = agent.run_generation(config=config)
            
            if success:
                print("✅ Synthetic data generation completed successfully")
                return True
            else:
                print("❌ Synthetic data generation failed")
                return False
                
        except Exception as e:
            logger.error(f"Error in synthetic data generation: {str(e)}")
            print(f"❌ Synthetic data generation failed: {str(e)}")
            return False
    
    def run_business_logic_generation(self) -> bool:
        """Run business logic generation step."""
        print("\n🔧 STEP 2: BUSINESS LOGIC GENERATION")
        print("-" * 50)
        
        try:
            agent = LibraryGeneratorAgent(self.run_id, mode="data_analysis")
            success = agent.generate_from_data_analysis()
            
            if success:
                print("✅ Business logic generation completed successfully")
                return True
            else:
                print("❌ Business logic generation failed")
                return False
                
        except Exception as e:
            logger.error(f"Error in business logic generation: {str(e)}")
            print(f"❌ Business logic generation failed: {str(e)}")
            return False
    
    def run_validation(self) -> bool:
        """Run validation step."""
        print("\n🔍 STEP 3: VALIDATION")
        print("-" * 50)
        
        try:
            agent = ValidationAgent(self.run_id)
            success = agent.run_validation()
            
            if success:
                print("✅ Validation completed successfully")
                return True
            else:
                print("❌ Validation failed")
                return False
                
        except Exception as e:
            logger.error(f"Error in validation: {str(e)}")
            print(f"❌ Validation failed: {str(e)}")
            return False
    
    def run_test_scenario_generation(self) -> bool:
        """Run test scenario data generation step (optional)."""
        print("\n🧪 STEP 4: TEST SCENARIO DATA GENERATION (OPTIONAL)")
        print("-" * 50)
        
        try:
            if self.journey == "1":
                # For Synthetic Data Generation, ask user if they want to run test scenario generation
                response = input("Do you want to run test scenario data generation? (y/n): ").strip().lower()
                
                if response in ['y', 'yes']:
                    agent = TestScenarioDataGeneratorAgent(self.run_id)
                    agent.run()
                    print("✅ Test scenario data generation completed")
                    return True
                else:
                    print("⏭️ Skipping test scenario data generation")
                    return True
            else:
                # For Functional Test Scenario Generation, this is a required step
                print("Running test scenario data generation...")
                agent = TestScenarioDataGeneratorAgent(self.run_id)
                agent.run()
                print("✅ Test scenario data generation completed")
                return True
                
        except Exception as e:
            logger.error(f"Error in test scenario generation: {str(e)}")
            print(f"❌ Test scenario generation failed: {str(e)}")
            return False
    
    def generate_summary_report(self):
        """Generate a summary report of the pipeline run."""
        print("\n📊 PIPELINE SUMMARY REPORT")
        print("="*80)
        print(f"Run ID: {self.run_id}")
        print(f"Journey: {self.journey}")
        print(f"Run Directory: {self.run_dir}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check what files were generated
        print("\n📁 Generated Files:")
        
        # Schema files
        schema_dir = os.path.join(self.run_dir, "schema")
        if os.path.exists(schema_dir):
            schema_files = os.listdir(schema_dir)
            print(f"  📋 Schema Analysis ({len(schema_files)} files):")
            for file in schema_files:
                print(f"    - {file}")
        
        # Input data files (for Functional Test Scenario Generation)
        input_data_dir = os.path.join(self.run_dir, "input_data")
        if os.path.exists(input_data_dir):
            input_files = [f for f in os.listdir(input_data_dir) if f.endswith('.csv')]
            if input_files:
                print(f"  📥 Input Data ({len(input_files)} files):")
                for file in input_files:
                    print(f"    - {file}")
        
        # Synthetic data files (for Synthetic Data Generation)
        synthetic_data_dir = os.path.join(self.run_dir, "synthetic_data")
        if os.path.exists(synthetic_data_dir):
            data_files = [f for f in os.listdir(synthetic_data_dir) if f.endswith('.csv')]
            if data_files:
                print(f"  🔧 Synthetic Data ({len(data_files)} files):")
                for file in data_files:
                    file_path = os.path.join(synthetic_data_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"    - {file} ({file_size:,} bytes)")
        
        # Validation files
        validation_dir = os.path.join(self.run_dir, "validation")
        if os.path.exists(validation_dir):
            validation_files = os.listdir(validation_dir)
            print(f"  🔍 Validation ({len(validation_files)} files):")
            for file in validation_files:
                print(f"    - {file}")
        
        print("\n🎉 Pipeline completed successfully!")
        print(f"📁 All outputs saved to: {self.run_dir}")
    
    def run_complete_pipeline(self) -> bool:
        """Run the complete pipeline based on the selected journey."""
        print("🚀 AI-Powered Test Data Generation Pipeline")
        print("="*80)
        print(f"🎯 Journey: {'Synthetic Data Generation' if self.journey == '1' else 'Functional Test Scenario Generation'}")
        print(f"📊 Run ID: {self.run_id}")
        print("="*80)
        
        logger.info(f"🚀 Initializing AI-powered pipeline for journey: {self.journey}")
        
        if self.journey == "1":
            success = self.run_journey_1()
        elif self.journey == "2":
            success = self.run_journey_2()
        else:
            logger.error(f"❌ Invalid journey: {self.journey}")
            print(f"❌ Invalid journey: {self.journey}")
            return False
        
        if success:
            logger.info("🎉 Pipeline completed successfully")
            # Generate summary report
            self.generate_summary_report()
        else:
            logger.error("❌ Pipeline failed")
        
        return success

def main():
    """Main function to run the complete pipeline."""
    try:
        print("🎯 Test Data Environment - Pipeline Orchestrator")
        print("="*60)
        print("Select User Journey:")
        print("1. Synthetic Data Generation: Schema-only → Full pipeline")
        print("   (Schema analysis + test scenarios + business logic → synthetic data → validation)")
        print("2. Functional Test Scenario Generation: Data + Schema → Business logic → Test scenarios → Validation")
        print("   (Schema analysis only → business logic generation → test scenario generation → validation)")
        
        while True:
            journey = input("\nEnter journey (1 or 2): ").strip()
            if journey in ["1", "2"]:
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
        
        # Check if user wants to specify a run ID
        run_id = input("Enter custom run ID (or press Enter for auto-generated): ").strip()
        if not run_id:
            run_id = None
        
        # Create and run the pipeline
        orchestrator = PipelineOrchestrator(run_id, journey)
        success = orchestrator.run_complete_pipeline()
        
        if success:
            print("\n✅ Pipeline completed successfully!")
            return 0
        else:
            print("\n❌ Pipeline failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n👋 Pipeline interrupted by user.")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in pipeline: {str(e)}")
        print(f"\n❌ Pipeline failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 