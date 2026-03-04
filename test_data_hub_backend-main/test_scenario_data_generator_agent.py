#!/usr/bin/env python3
"""
Test Scenario Data Generator Agent

This agent generates synthetic data for specific test scenarios from the business logic library
and creates new synthetic data files (not appending to existing data).
"""

import os
import sys
import json
import csv
import logging
import pandas as pd
from typing import List, Dict, Any, Tuple
import openai
from datetime import datetime, timedelta
import random
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import OPENAI_API_KEY
from run_id_manager import generate_run_id, list_runs, get_run_info

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

class TestScenarioDataGeneratorAgent:
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
        self.input_schema_dir = os.path.join(self.input_data_dir, "schema")
        self.input_data_files_dir = os.path.join(self.input_data_dir, "data")
        self.schema_dir = os.path.join(self.run_dir, "schema")
        self.synthetic_data_dir = os.path.join(self.run_dir, "synthetic_data")
        self.validation_dir = os.path.join(self.run_dir, "validation")
        
        # Load run configuration if available
        self.run_config = self.load_run_config()
        
        # Create directory structure
        self.create_directory_structure()
        
        self.business_logic_dir = "business_logic_library"
        self.test_scenarios_file = os.path.join(self.business_logic_dir, "test_scenarios.csv")
        self.business_rules_file = os.path.join(self.business_logic_dir, "business_rules.csv")
        self.schema_analysis_file = os.path.join(self.schema_dir, "schema_analysis_results.json")
        
    def load_run_config(self) -> Dict[str, Any]:
        """Load the run configuration file if it exists."""
        try:
            config_file = os.path.join(self.run_dir, "run_config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"✅ Loaded run configuration for run {self.run_id}")
                    logger.info(f"   Product: {config.get('product_type', 'unknown')}")
                    logger.info(f"   Source: {config.get('source_type', 'unknown')}")
                    return config
            else:
                logger.warning(f"⚠️ No run configuration found at {config_file}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error loading run configuration: {e}")
            return {}
    
    def create_directory_structure(self):
        """Create the directory structure for this run."""
        directories = [
            self.run_dir,
            self.input_data_dir,
            self.input_schema_dir,
            self.input_data_files_dir,
            self.schema_dir,
            self.synthetic_data_dir,
            os.path.join(self.synthetic_data_dir, "data"),      # For CSV files
            os.path.join(self.synthetic_data_dir, "scripts"),   # For Python files
            self.validation_dir,
            os.path.join(self.validation_dir, "reports"),       # For JSON/TXT reports
            os.path.join(self.validation_dir, "scripts")        # For Python files
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
    def load_test_scenarios(self) -> List[Dict[str, Any]]:
        """Load test scenarios from the library."""
        try:
            scenarios = []
            logger.info(f"Loading test scenarios from: {self.test_scenarios_file}")
            
            if not os.path.exists(self.test_scenarios_file):
                logger.error(f"Test scenarios file not found: {self.test_scenarios_file}")
                return []
                
            with open(self.test_scenarios_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    try:
                        scenarios.append(row)
                    except Exception as row_error:
                        logger.error(f"Error processing row {i}: {row_error}")
                        logger.error(f"Row content: {row}")
                        continue
                        
            logger.info(f"Loaded {len(scenarios)} test scenarios from library")
            return scenarios
        except Exception as e:
            logger.error(f"Error loading test scenarios: {str(e)}")
            logger.error(f"File path: {self.test_scenarios_file}")
            return []
    
    def load_business_rules(self) -> List[Dict[str, Any]]:
        """Load business rules from the library."""
        try:
            rules = []
            logger.info(f"Loading business rules from: {self.business_rules_file}")
            
            if not os.path.exists(self.business_rules_file):
                logger.error(f"Business rules file not found: {self.business_rules_file}")
                return []
                
            with open(self.business_rules_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    try:
                        rules.append(row)
                    except Exception as row_error:
                        logger.error(f"Error processing row {i}: {row_error}")
                        logger.error(f"Row content: {row}")
                        continue
                        
            logger.info(f"Loaded {len(rules)} business rules from library")
            return rules
        except Exception as e:
            logger.error(f"Error loading business rules: {str(e)}")
            logger.error(f"File path: {self.business_rules_file}")
            return []
    
    def load_input_data(self) -> Dict[str, pd.DataFrame]:
        """Load input data files for referential integrity."""
        try:
            input_data = {}
            
            if not os.path.exists(self.input_data_files_dir):
                logger.warning(f"Input data directory {self.input_data_files_dir} not found")
                return {}
                
            for file in os.listdir(self.input_data_files_dir):
                if file.endswith('.csv'):
                    table_name = file.replace('.csv', '')
                    file_path = os.path.join(self.input_data_files_dir, file)
                    df = pd.read_csv(file_path)
                    input_data[table_name] = df
                    logger.info(f"Loaded input data for {table_name}: {len(df)} records")
            
            return input_data
        except Exception as e:
            logger.error(f"Error loading input data: {str(e)}")
            return {}
    
    def load_input_data_from_directory(self, directory_path: str) -> Dict[str, pd.DataFrame]:
        """Load input data from a specific directory."""
        input_data = {}
        if not os.path.exists(directory_path):
            logger.warning(f"Input data directory not found at {directory_path}")
            return {}
        
        for file in os.listdir(directory_path):
            if file.endswith('.csv'):
                table_name = file.replace('.csv', '')
                file_path = os.path.join(directory_path, file)
                df = pd.read_csv(file_path)
                input_data[table_name] = df
                logger.info(f"Loaded input data for {table_name} from {directory_path}: {len(df)} records")
        return input_data
    
    def load_schema_analysis(self) -> Dict[str, Any]:
        """Load schema analysis results for context."""
        try:
            with open(self.schema_analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            logger.info("Loaded schema analysis results")
            return analysis
        except Exception as e:
            logger.error(f"Error loading schema analysis: {str(e)}")
            return {}
    
    def display_test_scenarios(self, scenarios: List[Dict[str, Any]]) -> None:
        """Display available test scenarios with record numbers."""
        print("\n" + "="*80)
        print("AVAILABLE TEST SCENARIOS")
        print("="*80)
        
        # Group by table
        tables = {}
        for i, scenario in enumerate(scenarios, 1):
            table = scenario['table_name']
            if table not in tables:
                tables[table] = []
            tables[table].append((i, scenario))
        
        for table_name in sorted(tables.keys()):
            print(f"\n📋 {table_name.upper()}:")
            print("-" * 60)
            for record_num, scenario in tables[table_name]:
                priority = scenario.get('priority', 'MEDIUM')
                scenario_type = scenario.get('scenario_type', 'positive')
                print(f"  {record_num:3d}. [{priority:8s}] [{scenario_type:8s}] {scenario['scenario_name']}")
                print(f"       Description: {scenario['description']}")
                print()
    
    def get_user_selection(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get user selection of test scenarios."""
        print("\n" + "="*60)
        print("SELECTION INSTRUCTIONS")
        print("="*60)
        print("Enter record numbers separated by commas (e.g., 1,5,12)")
        print("Or enter ranges (e.g., 1-5, 10-15)")
        print("Type 'all' to select all scenarios")
        print("Type 'quit' to exit")
        print("="*60)
        
        while True:
            try:
                selection = input("\nEnter your selection: ").strip()
                
                if selection.lower() == 'quit':
                    return []
                elif selection.lower() == 'all':
                    return scenarios
                
                selected_scenarios = []
                parts = selection.split(',')
                
                for part in parts:
                    part = part.strip()
                    if '-' in part:
                        # Range selection
                        start, end = map(int, part.split('-'))
                        for i in range(start, end + 1):
                            if 1 <= i <= len(scenarios):
                                selected_scenarios.append(scenarios[i-1])
                    else:
                        # Single selection
                        record_num = int(part)
                        if 1 <= record_num <= len(scenarios):
                            selected_scenarios.append(scenarios[record_num-1])
                
                if selected_scenarios:
                    print(f"\n✅ Selected {len(selected_scenarios)} test scenarios:")
                    for i, scenario in enumerate(selected_scenarios, 1):
                        print(f"  {i}. [{scenario['table_name']}] {scenario['scenario_name']}")
                    return selected_scenarios
                else:
                    print("❌ No valid scenarios selected. Please try again.")
                    
            except ValueError:
                print("❌ Invalid input. Please enter numbers separated by commas.")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def get_generation_config(self) -> Dict[str, Any]:
        """Get data generation configuration from user."""
        print("\n" + "="*60)
        print("DATA GENERATION CONFIGURATION")
        print("="*60)
        
        config = {}
        
        # Default records per scenario
        while True:
            try:
                default_records = input("Default number of records per scenario (default: 5): ").strip()
                if not default_records:
                    config['default_records'] = 5
                    break
                else:
                    config['default_records'] = int(default_records)
                    if config['default_records'] > 0:
                        break
                    else:
                        print("❌ Number of records must be positive.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Priority-based multipliers
        print("\nPriority-based record multipliers:")
        config['priority_multipliers'] = {}
        
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            while True:
                try:
                    multiplier = input(f"Multiplier for {priority} priority (default: 2.0 for CRITICAL, 1.5 for HIGH, 1.0 for others): ").strip()
                    if not multiplier:
                        if priority == 'CRITICAL':
                            config['priority_multipliers'][priority] = 2.0
                        elif priority == 'HIGH':
                            config['priority_multipliers'][priority] = 1.5
                        else:
                            config['priority_multipliers'][priority] = 1.0
                        break
                    else:
                        config['priority_multipliers'][priority] = float(multiplier)
                        if config['priority_multipliers'][priority] > 0:
                            break
                        else:
                            print("❌ Multiplier must be positive.")
                except ValueError:
                    print("❌ Please enter a valid number.")
        
        return config
    
    def generate_test_data_code(self, selected_scenarios: List[Dict[str, Any]], 
                               input_data: Dict[str, pd.DataFrame],
                               schema_analysis: Dict[str, Any],
                               business_rules: List[Dict[str, Any]],
                               config: Dict[str, Any]) -> str:
        """Generate Python code for creating test scenario data."""
        
        # Create context for the LLM
        context = self.create_generation_context(selected_scenarios, input_data, 
                                               schema_analysis, business_rules, config)
        
        # Generate the prompt
        prompt = self.create_generation_prompt(context)
        
        try:
            logger.info("Generating test data code using LLM...")
            
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert Python developer specializing in synthetic data generation for test scenarios. 
                        
CRITICAL REQUIREMENTS:
1. Write clean, efficient, and well-documented Python code
2. Ensure referential integrity with input data
3. Follow business rules and constraints
4. Generate data that satisfies the specific test scenario requirements
5. Use realistic data patterns and distributions
6. Handle edge cases and error conditions properly
7. Maintain data consistency across tables
8. Generate ONLY NEW test scenario data (do not append to existing data)

CODING STANDARDS:
- Use pandas for data manipulation
- Use faker for realistic data generation
- Use random for controlled randomness
- Handle all exceptions gracefully
- Add comprehensive comments
- Follow PEP 8 style guidelines"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=32000,
                temperature=0.1
            )
            
            generated_code = response.choices[0].message.content
            
            # Extract code from markdown if present
            if "```python" in generated_code:
                start = generated_code.find("```python") + 9
                end = generated_code.find("```", start)
                generated_code = generated_code[start:end].strip()
            
            logger.info("Successfully generated test data code")
            return generated_code
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise
    
    def create_generation_context(self, selected_scenarios: List[Dict[str, Any]], 
                                 input_data: Dict[str, pd.DataFrame],
                                 schema_analysis: Dict[str, Any],
                                 business_rules: List[Dict[str, Any]],
                                 config: Dict[str, Any]) -> Dict[str, Any]:
        """Create context for the LLM code generation."""
        
        # Extract business rules by table
        business_rules_by_table = {}
        for rule in business_rules:
            table = rule['table_name']
            if table not in business_rules_by_table:
                business_rules_by_table[table] = []
            business_rules_by_table[table].append(rule)
        
        # Extract input data statistics
        input_data_stats = {}
        for table_name, df in input_data.items():
            input_data_stats[table_name] = {
                'record_count': len(df),
                'columns': list(df.columns),
                'unique_values': {col: df[col].nunique() for col in df.columns if df[col].dtype == 'object'},
                'value_ranges': {col: {'min': df[col].min(), 'max': df[col].max()} 
                               for col in df.columns if df[col].dtype in ['int64', 'float64']}
            }
        
        return {
            'selected_scenarios': selected_scenarios,
            'input_data_stats': input_data_stats,
            'schema_analysis': schema_analysis,
            'business_rules_by_table': business_rules_by_table,
            'config': config
        }
    
    def create_generation_prompt(self, context: Dict[str, Any]) -> str:
        """Create the prompt for LLM code generation."""
        
        scenarios_text = "\n".join([
            f"  {i+1}. [{s['table_name']}] {s['scenario_name']}\n"
            f"     Type: {s['scenario_type']}, Priority: {s['priority']}\n"
            f"     Description: {s['description']}\n"
            f"     Test Conditions: {s['test_conditions']}\n"
            f"     Data Requirements: {s['data_requirements']}\n"
            for i, s in enumerate(context['selected_scenarios'])
        ])
        
        business_rules_text = ""
        for table, rules in context['business_rules_by_table'].items():
            business_rules_text += f"\n{table}:\n"
            for rule in rules:
                business_rules_text += f"  - {rule['rule_name']}: {rule['validation_logic']}\n"
        
        input_data_stats_text = ""
        for table, stats in context['input_data_stats'].items():
            input_data_stats_text += f"\n{table}:\n"
            input_data_stats_text += f"  Records: {stats['record_count']}\n"
            input_data_stats_text += f"  Columns: {', '.join(stats['columns'])}\n"
        
        prompt = f"""
TASK: Generate Python code to create NEW synthetic test data for specific test scenarios (do not append to existing data).

SELECTED TEST SCENARIOS:
{scenarios_text}

GENERATION CONFIGURATION:
- Default records per scenario: {context['config']['default_records']}
- Priority multipliers: {context['config']['priority_multipliers']}

INPUT DATA STATISTICS (for referential integrity):
{input_data_stats_text}

BUSINESS RULES BY TABLE:
{business_rules_text}

REQUIREMENTS:
1. Create a Python class called TestScenarioDataGenerator with __init__(self) constructor (no parameters)
2. The class should have a method generate_test_data() that:
   - Generates NEW data for each selected test scenario
   - Respects the priority multipliers for record counts
   - Ensures referential integrity with input data
   - Follows all business rules
   - Creates NEW CSV files in the synthetic_data_dir (do not append to existing files)
3. Use realistic data generation (faker, random)
4. Handle all test scenario types (positive, negative, edge_case)
5. Ensure data consistency and quality
6. Add comprehensive error handling and logging
7. Generate ONLY the test scenario data (not all data)

CRITICAL FILE PATH REQUIREMENTS:
- Use the module-level synthetic_data_dir variable for all file operations
- Use the module-level input_data_dir variable for reading input data
- Read input data from input_data_dir for referential integrity
- Write NEW CSV files to synthetic_data_dir/data (NOT directly to synthetic_data_dir)
- Use os.path.join(synthetic_data_dir, "data", filename) for output file paths
- Use os.path.join(input_data_dir, filename) for input file paths
- Do NOT use hardcoded file paths like "./input_data/"
- Do NOT require synthetic_data_dir or input_data_dir as constructor parameters
- Access synthetic_data_dir and input_data_dir directly from the module namespace

OUTPUT FORMAT:
- Generate only the Python class code
- No explanations or markdown formatting
- Code should be ready to execute
- Include all necessary imports

The generated code should create NEW test data that satisfies the specific requirements of each test scenario while maintaining data integrity and following business rules.

EXAMPLE FILE PATHS:
- To read input data: os.path.join(input_data_dir, "customer_info.csv")
- To write output data: os.path.join(synthetic_data_dir, "data", "customer_info.csv")
- Do NOT use: "./input_data/customer_info.csv" or hardcoded paths
- Do NOT write directly to synthetic_data_dir (must use synthetic_data_dir/data)
"""
        
        return prompt
    
    def execute_generated_code(self, generated_code: str, input_data: Dict[str, pd.DataFrame]) -> bool:
        """Execute the generated code to create test data."""
        try:
            # Create a permanent script file in the scripts directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_file = os.path.join(self.synthetic_data_dir, "scripts", f"test_scenario_generator_{timestamp}.py")
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(generated_code)
            
            logger.info(f"Generated script saved to: {script_file}")
            
            # Import and execute the generated code
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_scenario_generator", script_file)
            module = importlib.util.module_from_spec(spec)
            
            # Add input data and configuration to module namespace
            module.input_data = input_data
            module.synthetic_data_dir = self.synthetic_data_dir
            module.input_data_dir = self.input_data_files_dir
            module.os = os  # Add os module for file path operations
            
            # Execute the module
            spec.loader.exec_module(module)
            
            # Create instance and generate data
            if hasattr(module, 'TestScenarioDataGenerator'):
                generator = module.TestScenarioDataGenerator()
                if hasattr(generator, 'generate_test_data'):
                    generator.generate_test_data()
                    logger.info("Successfully executed test data generation")
                    return True
                else:
                    logger.error("Generated code missing generate_test_data method")
                    return False
            else:
                logger.error("Generated code missing TestScenarioDataGenerator class")
                return False
                
        except Exception as e:
            logger.error(f"Error during test data generation: {str(e)}")
            return False
    
    def run(self):
        """Main execution method."""
        print(f"\n🧪 AI-Powered Test Scenario Data Generation Engine")
        print(f"📊 Run ID: {self.run_id}")
        
        # Display run configuration info if available
        if self.run_config:
            product_type = self.run_config.get('product_type', 'unknown')
            source_type = self.run_config.get('source_type', 'unknown')
            print(f"🏷️ Product: {product_type}")
            print(f"📁 Source: {source_type}")
            
            # Show folder structure info
            target_subdir = self.run_config.get('folder_structure', {}).get('target_subdir', 'unknown')
            print(f"📂 Input Location: input_data/{target_subdir}")
            
            # Show file count if available
            files = self.run_config.get('files', [])
            if files:
                print(f"📄 Input Files: {len(files)} files loaded")
        
        print("="*60)
        
        logger.info(f"🚀 Initializing intelligent test scenario data generation for run: {self.run_id}")
        
        try:
            # Load all necessary data
            print("\n📋 STEP 1: Loading Test Scenarios & Business Logic")
            logger.info("🔍 Loading test scenarios and business rules from library...")
            scenarios = self.load_test_scenarios()
            business_rules = self.load_business_rules()
            
            if not scenarios:
                logger.error("❌ No test scenarios found in library")
                print("❌ No test scenarios found in library.")
                return
            
            logger.info(f"✅ Loaded {len(scenarios)} test scenarios and {len(business_rules)} business rules")
            print(f"   📊 Test scenarios: {len(scenarios)} | Business rules: {len(business_rules)}")
            
            print("\n📋 STEP 2: Loading Input Data & Schema Analysis")
            logger.info("🔍 Loading input data and schema analysis for context...")
            
            # Use run configuration to determine input data source
            input_data = {}
            if self.run_config and self.run_config.get('folder_structure', {}).get('target_subdir'):
                target_subdir = self.run_config['folder_structure']['target_subdir']
                logger.info(f"🔍 Looking for input data in run-specific directory: input_data/{target_subdir}")
                
                # Try to load from run-specific input data first
                if target_subdir == 'data':
                    input_data = self.load_input_data_from_directory(self.input_data_files_dir)
                elif target_subdir == 'schema':
                    input_data = self.load_input_data_from_directory(self.input_schema_dir)
                
                if input_data:
                    logger.info(f"✅ Loaded {len(input_data)} input data tables from run directory")
            
            # Fallback to original input data loading if no data found in run directory
            if not input_data:
                logger.info("🔍 Fallback: Loading from original input data directories")
                input_data = self.load_input_data()
            
            schema_analysis = self.load_schema_analysis()
            
            if not input_data:
                logger.error("❌ No input data found")
                print("❌ No input data found. Please ensure input data is available in the run.")
                return
            
            logger.info(f"✅ Loaded {len(input_data)} input data tables")
            print(f"   📊 Input data tables: {', '.join(input_data.keys())}")
            
            # Display available scenarios
            print("\n📋 STEP 3: Test Scenario Selection")
            logger.info("🎯 Displaying available test scenarios for user selection...")
            self.display_test_scenarios(scenarios)
            
            # Get user selection
            selected_scenarios = self.get_user_selection(scenarios)
            if not selected_scenarios:
                logger.info("👋 No scenarios selected by user")
                print("👋 No scenarios selected. Exiting...")
                return
            
            logger.info(f"✅ User selected {len(selected_scenarios)} test scenarios")
            
            # Get generation configuration
            print("\n⚙️ STEP 4: Generation Configuration")
            logger.info("⚙️ Collecting data generation configuration from user...")
            config = self.get_generation_config()
            logger.info(f"✅ Configuration set: {config['default_records']} default records, priority multipliers configured")
            
            # Generate and execute code
            print("\n🤖 STEP 5: AI Test Data Generation")
            logger.info("🚀 Engaging OpenAI GPT-4 for intelligent test data generation...")
            print("   🔄 AI is generating sophisticated test scenario data...")
            generated_code = self.generate_test_data_code(
                selected_scenarios, input_data, schema_analysis, business_rules, config
            )
            
            logger.info("✅ AI test data generation code created")
            print("   ✅ Intelligent test data generation logic created")
            
            print("\n⚡ STEP 6: Test Data Generation Execution")
            logger.info("🚀 Executing AI-generated test scenario data generation...")
            print("   🔄 Generating test scenario data with business logic compliance...")
            success = self.execute_generated_code(generated_code, input_data)
            
            if success:
                logger.info("🎉 Test scenario data generation completed successfully")
                print("   ✅ Test scenario data generation completed successfully!")
                print(f"   📁 Check the generated files in: {os.path.join(self.synthetic_data_dir, 'data')}")
            else:
                logger.error("❌ Test scenario data generation failed")
                print("   ❌ Test scenario data generation failed.")
                
        except KeyboardInterrupt:
            logger.info("👋 Operation cancelled by user")
            print("\n\n👋 Operation cancelled by user.")
        except Exception as e:
            logger.error(f"❌ Error in main execution: {str(e)}")
            print(f"\n❌ Error: {str(e)}")

def main():
    """Main function to run the test scenario data generator agent."""
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
        print("\n🧪 Test Scenario Data Generator Agent")
        print("="*50)
        print("Select a run ID that has schema analysis and input data:")
        
        if existing_runs:
            print(f"Available runs: {', '.join(existing_runs)}")
            run_id = input("Enter run ID: ").strip()
            
            if not run_id or not run_id.isdigit():
                print("Invalid run ID. Please enter a valid number.")
                return
            
            # Check if run exists and has schema analysis
            info = get_run_info(run_id)
            if not info:
                print(f"Run {run_id} does not exist.")
                return
            
            if not info["has_schema"]:
                print(f"Run {run_id} does not have schema analysis. Please run schema analysis first.")
                return
        else:
            print("No existing runs found. Please run schema analysis first.")
            return
        
        # Initialize the agent with the selected run ID
        agent = TestScenarioDataGeneratorAgent(run_id=run_id)
        agent.run()
        
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 