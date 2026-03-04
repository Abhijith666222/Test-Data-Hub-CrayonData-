import os
import json
import logging
import pandas as pd
import openai
from config import OPENAI_API_KEY
from datetime import datetime
from run_id_manager import generate_run_id, list_runs, get_run_info

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

class ValidationAgent:
    def __init__(self, run_id: str = None):
        # Generate unique run ID if not provided
        if run_id is None:
            self.run_id = generate_run_id()
        else:
            self.run_id = run_id
        
        # Define folder structure
        self.base_dir = "runs"
        self.run_dir = os.path.join(self.base_dir, self.run_id)
        self.input_data_dir = os.path.join(self.run_dir, "input_data")
        self.schema_dir = os.path.join(self.run_dir, "schema")
        self.synthetic_data_dir = os.path.join(self.run_dir, "synthetic_data")
        self.validation_dir = os.path.join(self.run_dir, "validation")
        
        # Create directory structure
        self.create_directory_structure()
        
        self.analysis_results = None
        
    def create_directory_structure(self):
        """Create the directory structure for this run."""
        directories = [
            self.run_dir,
            self.input_data_dir,
            self.schema_dir,
            self.synthetic_data_dir,
            self.validation_dir,
            os.path.join(self.validation_dir, "reports"),    # For JSON/TXT reports
            os.path.join(self.validation_dir, "scripts")     # For Python files
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def load_analysis_results(self, analysis_file: str = None):
        """Load the schema analysis results."""
        try:
            if analysis_file is None:
                # Look for analysis results in the schema directory
                analysis_file = os.path.join(self.schema_dir, "schema_analysis_results.json")
            
            with open(analysis_file, 'r', encoding='utf-8') as f:
                self.analysis_results = json.load(f)
            logger.info("Loaded schema analysis results successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading analysis results: {str(e)}")
            return False
    
    def load_generated_data(self):
        """Load all generated CSV files."""
        data_files = {}
        try:
            data_dir = os.path.join(self.synthetic_data_dir, "data")
            if not os.path.exists(data_dir):
                logger.error(f"Data directory {data_dir} not found")
                return None
                
            for filename in os.listdir(data_dir):
                if filename.endswith('.csv'):
                    table_name = filename.replace('.csv', '')
                    file_path = os.path.join(data_dir, filename)
                    data_files[table_name] = pd.read_csv(file_path)
                    logger.info(f"Loaded {table_name}: {len(data_files[table_name])} rows")
            return data_files
        except Exception as e:
            logger.error(f"Error loading generated data: {str(e)}")
            return None
    
    def generate_validation_prompt(self, data_files):
        """Generate the prompt for LLM to create validation code."""
        
        # Extract business rules and test scenarios
        business_rules = self.analysis_results.get('business_rules', {})
        test_scenarios = self.analysis_results.get('test_scenarios', {})
        
        # Create data summary for each table
        data_summary = {}
        for table_name, df in data_files.items():
            data_summary[table_name] = {
                'row_count': len(df),
                'columns': list(df.columns),
                'sample_data': df.head(3).to_dict('records'),
                'data_types': {col: str(dtype) for col, dtype in df.dtypes.to_dict().items()}
            }
        
        prompt = f"""
You are an expert data validation engineer. Create a comprehensive validation script that validates the generated synthetic data against business rules and test scenarios.

ANALYSIS RESULTS:
{json.dumps(self.analysis_results, indent=2)}

GENERATED DATA SUMMARY:
{json.dumps(data_summary, indent=2)}

REQUIREMENTS:
1. Create a DataValidator class with methods to validate each table
2. Implement business rule validations for each table
3. Implement test scenario validations (positive, negative, edge cases)
4. Generate detailed validation reports
5. Handle cross-table relationship validations
6. Provide clear pass/fail status for each validation
7. Include data quality metrics

VALIDATION REQUIREMENTS:

1. BUSINESS RULES VALIDATION:
   - Age restrictions and validations
   - Credit limit validations
   - Transaction limit validations
   - Account status validations
   - Date range validations
   - Business constraint validations

2. TEST SCENARIOS VALIDATION:
   - Positive scenarios (70% of data should pass)
   - Negative scenarios (20% of data should fail appropriately)
   - Edge cases (10% of data should test boundaries)
   - Expired cards validation
   - Blocked accounts validation
   - Failed transactions validation

3. CROSS-TABLE VALIDATION:
   - Foreign key relationships
   - Referential integrity
   - Business logic consistency across tables

OUTPUT REQUIREMENTS:
1. Create a DataValidator class with:
   - __init__(self, data_files, business_rules, test_scenarios, cross_table_relationships)
   - validate_all_tables(self)
   - validate_table(self, table_name)
   - validate_business_rules(self, table_name)
   - validate_test_scenarios(self, table_name)
   - validate_cross_table_relationships(self)
   - generate_validation_report(self)
   - save_validation_results(self, output_path)

2. The validation report should include:
   - Overall validation status (PASS/FAIL)
   - Per-table validation results
   - Business rule validation results
   - Test scenario validation results
   - Cross-table validation results
   - Detailed error messages for failures
   - Summary statistics

3. Save results to:
   - validation_report.json (detailed results)
   - validation_summary.txt (human-readable summary)

CRITICAL CODING RULES:
1. Use pandas for data manipulation
2. Implement proper error handling
3. Use clear, descriptive validation messages
4. Handle missing data gracefully
5. Provide detailed failure reasons
6. Focus ONLY on business logic and test scenario validation
7. Implement efficient validation logic
8. Handle edge cases properly

Create a complete, runnable Python script that can be executed directly. The script should be well-documented, handle errors gracefully, and provide comprehensive validation results.
"""
        return prompt
    
    def call_openai_for_validation_code(self, prompt):
        """Call OpenAI API to generate validation code."""
        try:
            logger.info("Generating validation code using LLM...")
            
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert data validation engineer specializing in creating comprehensive validation scripts. Write clean, efficient, and well-documented Python code that can be executed directly.

CRITICAL CODING RULES:
1. ALWAYS use pandas for data manipulation and validation
2. Implement proper error handling with try-catch blocks
3. Use clear, descriptive validation messages
4. Handle missing data gracefully with .isna() checks
5. Provide detailed failure reasons for each validation
6. Focus ONLY on business logic and test scenario validation
7. Implement efficient validation logic with vectorized operations
8. Handle edge cases properly
9. Use datetime for date/time validations
10. Implement proper logging for validation results

VALIDATION PATTERNS:
- Use df[condition].shape[0] for counting records
- Use df[column].between(min_val, max_val) for range checks
- Use pd.to_datetime() for date validations
- Use df.merge() for relationship validations
- Focus on business rule compliance
- Validate test scenario implementation"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=32000,
                temperature=0.1
            )
            
            validation_code = response.choices[0].message.content
            
            # Extract code from markdown if present
            if "```python" in validation_code:
                start = validation_code.find("```python") + 9
                end = validation_code.find("```", start)
                validation_code = validation_code[start:end].strip()
            
            logger.info("Validation code generated successfully")
            return validation_code
            
        except Exception as e:
            logger.error(f"Error generating validation code: {str(e)}")
            return None
    
    def save_validation_code(self, validation_code):
        """Save the generated validation code."""
        try:
            output_file = os.path.join(self.validation_dir, "scripts", "generated_validator.py")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(validation_code)
            logger.info(f"Validation code saved to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving validation code: {str(e)}")
            return None
    
    def execute_validation(self, validation_code_file):
        """Execute the generated validation code."""
        try:
            logger.info("Executing validation code...")
            
            # Import and execute the generated validation code
            import importlib.util
            spec = importlib.util.spec_from_file_location("validator", validation_code_file)
            validator_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validator_module)
            
            # Load data files
            data_files = self.load_generated_data()
            if not data_files:
                raise Exception("Failed to load generated data")
            
            # Extract business rules and test scenarios by table
            business_rules_by_table = {}
            test_scenarios_by_table = {}
            
            for table_info in self.analysis_results.get('tables', []):
                table_name = table_info.get('table_name')
                if table_name:
                    business_rules_by_table[table_name] = table_info.get('business_rules', [])
                    test_scenarios_by_table[table_name] = table_info.get('test_scenarios', [])
            
            # Create a custom DataValidator class that doesn't call load_data in __init__
            class CustomDataValidator(validator_module.DataValidator):
                def __init__(self, data_files, business_rules, test_scenarios, cross_table_relationships):
                    # Initialize without calling load_data
                    self.data_files = data_files
                    self.business_rules = business_rules
                    self.test_scenarios = test_scenarios
                    self.cross_table_relationships = cross_table_relationships
                    self.data = {}
                    self.validation_results = {
                        'overall_status': 'PASS',
                        'tables': {},
                        'cross_table': [],
                        'summary': {}
                    }
                    # Don't call load_data here - we'll handle it manually
            
            # Create validator instance and run validation
            validator = CustomDataValidator(
                data_files=data_files,  # This contains DataFrames, not file paths
                business_rules=business_rules_by_table,
                test_scenarios=test_scenarios_by_table,
                cross_table_relationships=self.analysis_results.get('cross_table_relationships', [])
            )
            
            # Directly assign the DataFrames to the data attribute
            validator.data = data_files
            
            # Run validation
            validation_results = validator.validate_all_tables()
            
            # Save results
            validator.save_validation_results(os.path.join(self.validation_dir, "reports"))
            
            logger.info("Validation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing validation: {str(e)}")
            return False
    
    def run_validation(self):
        """Main method to run the validation process."""
        print(f"\n🔍 AI-Powered Data Validation Engine")
        print(f"📊 Run ID: {self.run_id}")
        print("="*60)
        
        logger.info(f"🚀 Initializing intelligent data validation for run: {self.run_id}")
        
        # Load analysis results
        print("\n📋 STEP 1: Loading Business Rules & Test Scenarios")
        logger.info("🔍 Loading AI-generated business rules and test scenarios...")
        if not self.load_analysis_results():
            logger.error("❌ Failed to load analysis results")
            return False
        
        logger.info("✅ Business rules and test scenarios loaded")
        
        # Load generated data
        print("\n📋 STEP 2: Loading Data for Validation")
        logger.info("🔍 Loading synthetic data for comprehensive validation...")
        data_files = self.load_generated_data()
        if not data_files:
            logger.error("❌ Failed to load synthetic data")
            return False
        
        logger.info(f"✅ Loaded {len(data_files)} data tables for validation")
        print(f"   📊 Data tables loaded: {', '.join(data_files.keys())}")
        
        # Generate validation prompt
        print("\n🤖 STEP 3: AI Validation Logic Generation")
        logger.info("🚀 Engaging OpenAI GPT-4 for intelligent validation logic...")
        print("   🔄 AI is generating sophisticated validation rules...")
        prompt = self.generate_validation_prompt(data_files)
        
        # Generate validation code using LLM
        validation_code = self.call_openai_for_validation_code(prompt)
        if not validation_code:
            logger.error("❌ Failed to generate validation code")
            return False
        
        logger.info("✅ AI validation code generation completed")
        print("   ✅ Intelligent validation logic created")
        
        # Save validation code
        print("\n💾 STEP 4: Validation Code Persistence")
        logger.info("💾 Saving AI-generated validation code...")
        validation_code_file = self.save_validation_code(validation_code)
        if not validation_code_file:
            logger.error("❌ Failed to save validation code")
            return False
        
        logger.info(f"✅ Validation code saved to: {validation_code_file}")
        
        # Execute validation
        print("\n⚡ STEP 5: Data Validation Execution")
        logger.info("🚀 Executing comprehensive data validation...")
        print("   🔄 Validating data against business rules and test scenarios...")
        success = self.execute_validation(validation_code_file)
        
        if success:
            logger.info("Validation process completed successfully")
            print("\n" + "="*50)
            print("VALIDATION COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"Run ID: {self.run_id}")
            print(f"Validation results: {self.validation_dir}")
            print(f"Generated validator: {validation_code_file}")
            print(f"Validation report: {os.path.join(self.validation_dir, 'reports', 'validation_report.json')}")
            print("="*50)
            
            # Display key validation results
            try:
                with open(os.path.join(self.validation_dir, 'reports', 'validation_report.json'), 'r') as f:
                    report = json.load(f)
                
                print(f"\nOVERALL STATUS: {report.get('overall_status', 'UNKNOWN')}")
                print(f"TABLES VALIDATED: {len(report.get('tables', {}))}")
                print(f"CROSS-TABLE RELATIONSHIPS: {len(report.get('cross_table', []))}")
                
                # Show table statuses
                print("\nTABLE VALIDATION RESULTS:")
                for table, result in report.get('tables', {}).items():
                    status = result.get('status', 'UNKNOWN')
                    print(f"  {table}: {status}")
                
                # Show cross-table validation results
                print("\nCROSS-TABLE RELATIONSHIP RESULTS:")
                for rel in report.get('cross_table', []):
                    relationship = rel.get('relationship', 'Unknown')
                    status = rel.get('status', 'UNKNOWN')
                    print(f"  {relationship}: {status}")
                    
            except Exception as e:
                logger.warning(f"Could not display validation results: {str(e)}")
                
        else:
            logger.error("Validation process failed")
        
        return success

def main():
    """Main function to run the validation agent."""
    try:
        # Show existing runs
        existing_runs = list_runs()
        if existing_runs:
            print("\n📊 Existing Runs:")
            for run_id in existing_runs[-5:]:  # Show last 5 runs
                info = get_run_info(run_id)
                if info:
                    status = []
                    if info["has_schema"]: status.append("📋 Schema")
                    if info["has_synthetic_data"]: status.append("🔧 Data")
                    if info["has_validation"]: status.append("🔍 Validation")
                    if info["has_input_data"]: status.append("📥 Input")
                    print(f"  Run {run_id}: {' | '.join(status) if status else 'Empty'}")
        
        # Ask user to select a run ID
        print("\n🔍 Validation Agent")
        print("="*50)
        print("Select a run ID that has synthetic data generated:")
        
        if existing_runs:
            print(f"Available runs: {', '.join(existing_runs)}")
            run_id = input("Enter run ID: ").strip()
            
            if not run_id or not run_id.isdigit():
                print("Invalid run ID. Please enter a valid number.")
                return
            
            # Check if run exists and has synthetic data
            info = get_run_info(run_id)
            if not info:
                print(f"Run {run_id} does not exist.")
                return
            
            if not info["has_synthetic_data"]:
                print(f"Run {run_id} does not have synthetic data. Please run synthetic data generation first.")
                return
        else:
            print("No existing runs found. Please run synthetic data generation first.")
            return
        
        # Initialize the agent with the selected run ID
        agent = ValidationAgent(run_id=run_id)
        success = agent.run_validation()
        
        if not success:
            print("Validation failed. Check logs for details.")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 