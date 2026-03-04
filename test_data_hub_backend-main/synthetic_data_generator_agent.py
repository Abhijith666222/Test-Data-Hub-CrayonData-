import os
import json
import pandas as pd
from openai import OpenAI
from config import OPENAI_API_KEY
from typing import Dict, List, Any
import logging
import subprocess
import tempfile
import importlib.util
from datetime import datetime
from run_id_manager import generate_run_id, list_runs, get_run_info

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SyntheticDataGeneratorAgent:
    def __init__(self, api_key: str, run_id: str = None):
        """Initialize the Synthetic Data Generator Agent with OpenAI client."""
        self.client = OpenAI(api_key=api_key)
        
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
        
        # Load run configuration if available
        self.run_config = self.load_run_config()
        
        # Create directory structure
        self.create_directory_structure()
        
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
            self.schema_dir,
            self.synthetic_data_dir,
            os.path.join(self.synthetic_data_dir, "data"),      # For CSV files
            os.path.join(self.synthetic_data_dir, "scripts"),   # For Python files
            self.validation_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
    def load_analysis_results(self, analysis_file: str = None) -> Dict[str, Any]:
        """Load the schema analysis results."""
        try:
            if analysis_file is None:
                # Look for analysis results in the schema directory
                analysis_file = os.path.join(self.schema_dir, "schema_analysis_results.json")
            
            with open(analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analysis results: {str(e)}")
            return None
    
    def load_original_schemas(self) -> Dict[str, Any]:
        """Load original CSV schemas."""
        schemas = {}
        
        # Look for schema files in the original input_schemas directory
        schema_source_dir = "input_schemas"
        
        if not os.path.exists(schema_source_dir):
            logger.error(f"Input schemas directory {schema_source_dir} not found")
            return schemas
        
        for filename in os.listdir(schema_source_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(schema_source_dir, filename)
                schema = self.read_csv_schema(file_path)
                if schema:
                    schemas[schema['table_name']] = schema
                    logger.info(f"Loaded original schema for {filename}")
        
        return schemas
    
    def load_schemas_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """Load CSV schemas from a specific directory."""
        schemas = {}
        
        if not os.path.exists(directory_path):
            logger.warning(f"Directory {directory_path} does not exist")
            return schemas
        
        for filename in os.listdir(directory_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(directory_path, filename)
                schema = self.read_csv_schema(file_path)
                if schema:
                    schemas[schema['table_name']] = schema
                    logger.info(f"Loaded schema from run directory: {filename}")
        
        return schemas
    
    def load_schemas_for_tables(self, table_names: set) -> Dict[str, Any]:
        """Load CSV schemas only for specified table names."""
        schemas = {}
        
        # Look for schema files in the original input_schemas directory
        schema_source_dir = "input_schemas"
        
        if not os.path.exists(schema_source_dir):
            logger.error(f"Input schemas directory {schema_source_dir} not found")
            return schemas
        
        for filename in os.listdir(schema_source_dir):
            if filename.endswith('.csv'):
                table_name = filename.replace('.csv', '')
                # Only load schema if table is in the available tables list
                if table_name in table_names:
                    file_path = os.path.join(schema_source_dir, filename)
                    schema = self.read_csv_schema(file_path)
                    if schema:
                        schemas[table_name] = schema
                        logger.info(f"Loaded schema for available table: {filename}")
                else:
                    logger.debug(f"Skipping schema for table not in run: {filename}")
        
        return schemas
    
    def read_csv_schema(self, file_path: str) -> Dict[str, Any]:
        """Read and parse CSV schema file."""
        try:
            df = pd.read_csv(file_path)
            
            # Extract schema information
            schema = {
                "table_name": os.path.basename(file_path).replace('.csv', ''),
                "columns": []
            }
            
            # Handle different CSV structures
            num_rows = len(df)
            
            # Get column names (always first row)
            column_names = df.iloc[0].tolist()
            
            # Get data types (second row if available)
            data_types = df.iloc[1].tolist() if num_rows > 1 else ["string"] * len(column_names)
            
            # Get descriptions (third row if available, or use column names as descriptions)
            if num_rows > 2:
                descriptions = df.iloc[2].tolist()
            else:
                descriptions = column_names
            
            # Get sample values (fourth row if available)
            if num_rows > 3:
                sample_values = df.iloc[3].tolist()
            else:
                sample_values = [""] * len(column_names)
            
            for i, col_name in enumerate(column_names):
                if pd.notna(col_name) and col_name.strip():
                    schema["columns"].append({
                        "name": col_name.strip(),
                        "data_type": data_types[i] if i < len(data_types) and pd.notna(data_types[i]) else "string",
                        "description": descriptions[i] if i < len(descriptions) and pd.notna(descriptions[i]) else col_name.strip(),
                        "sample_values": sample_values[i] if i < len(sample_values) and pd.notna(sample_values[i]) else ""
                    })
            
            return schema
            
        except Exception as e:
            logger.error(f"Error reading schema file {file_path}: {str(e)}")
            return None
    
    def build_dependency_graph(self, analysis_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Build dependency graph from cross-table relationships."""
        dependencies = {}
        
        # Get available table names from analysis results
        available_tables = {table['table_name'] for table in analysis_results.get('tables', [])}
        
        # Initialize only available tables with empty dependencies
        for table in analysis_results['tables']:
            dependencies[table['table_name']] = []
        
        # Add dependencies from relationships (if available), but only for available tables
        if 'cross_table_relationships' in analysis_results and analysis_results['cross_table_relationships']:
            for relationship in analysis_results['cross_table_relationships']:
                from_table = relationship['from_table']
                to_table = relationship['to_table']
                
                # Only add relationships if both tables are available in this run
                if from_table in available_tables and to_table in available_tables:
                    if from_table not in dependencies:
                        dependencies[from_table] = []
                    dependencies[from_table].append(to_table)
                    logger.debug(f"Added dependency: {from_table} → {to_table}")
                else:
                    logger.debug(f"Skipping dependency {from_table} → {to_table} (table not in run)")
        else:
            logger.info("⚠️ No cross_table_relationships found, using default dependency order")
        
        logger.info(f"✅ Built dependency graph for {len(dependencies)} available tables: {list(dependencies.keys())}")
        return dependencies
    
    def get_generation_order(self, dependencies: Dict[str, List[str]]) -> List[str]:
        """Get generation order using topological sort."""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def dfs(node):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected: {node}")
            if node in visited:
                return
            
            temp_visited.add(node)
            
            for dep in dependencies.get(node, []):
                dfs(dep)
            
            temp_visited.remove(node)
            visited.add(node)
            order.append(node)
        
        for table in dependencies:
            if table not in visited:
                dfs(table)
        
        return order
    
    def generate_code_prompt(self, analysis_results: Dict[str, Any], original_schemas: Dict[str, Any], config: Dict[str, Any], generation_order: List[str]) -> str:
        """Generate prompt for LLM to create synthetic data generation code."""
        
        # Filter analysis_results to only include tables that have schemas
        available_table_names = set(original_schemas.keys())
        logger.info(f"🔍 Filtering analysis results to only include tables with schemas: {list(available_table_names)}")
        
        filtered_analysis = {
            'tables': [table for table in analysis_results.get('tables', []) 
                      if table['table_name'] in available_table_names],
            'cross_table_relationships': [rel for rel in analysis_results.get('cross_table_relationships', [])
                                        if rel['from_table'] in available_table_names and rel['to_table'] in available_table_names],
            'business_rules': analysis_results.get('business_rules', []),
            'test_scenarios': analysis_results.get('test_scenarios', [])
        }
        
        logger.info(f"✅ Filtered analysis contains {len(filtered_analysis['tables'])} tables: {[t['table_name'] for t in filtered_analysis['tables']]}")
        logger.info(f"✅ Filtered relationships: {len(filtered_analysis['cross_table_relationships'])} cross-table relationships")
        
        # Create combined schema information
        combined_schemas = {}
        for table in filtered_analysis['tables']:
            table_name = table['table_name']
            original_schema = original_schemas.get(table_name, {'columns': []})
            
            combined_schemas[table_name] = {
                'primary_key': table.get('primary_key', ''),
                'columns': original_schema.get('columns', []),
                'business_rules': table.get('business_rules', []),
                'test_scenarios': table.get('test_scenarios', []),
                'data_generation_rules': table.get('data_generation_rules', [])
            }
        
        prompt = f"""
You are an expert Python developer specializing in synthetic data generation. Create a comprehensive Python script that generates synthetic data based on the provided schema analysis and requirements.

FILTERED ANALYSIS RESULTS (Only tables with available schemas):
{json.dumps(filtered_analysis, indent=2)}

AVAILABLE SCHEMAS:
{json.dumps(original_schemas, indent=2)}

COMBINED SCHEMA INFORMATION:
{json.dumps(combined_schemas, indent=2)}

GENERATION CONFIGURATION:
{json.dumps(config, indent=2)}

GENERATION ORDER:
{generation_order}

CRITICAL: You MUST use this EXACT generation order. Do NOT change or hardcode a different order.
The order is: {' → '.join(generation_order)}

REQUIREMENTS:

1. Create a Python class called `SyntheticDataGenerator` that:
   - Generates data for all tables in the specified generation order
   - Respects business rules and constraints
   - Implements test scenarios
   - Uses the specified volume configuration

2. The generator should:
   - Generate data in the correct order based on dependencies
   - Ensure referential integrity across tables
   - Apply business rules during generation
   - Inject test scenarios according to the specified mix
   - Use realistic data patterns and distributions

3. Key Features:
   - Dynamic field generation based on generation rules
   - Business rule enforcement
   - Test scenario injection
   - Volume control
   - CSV output generation ONLY

4. Required Methods:
   - `__init__(self, config)`: Initialize with configuration
   - `generate_all_data(self)`: Generate data for all tables in order
   - `generate_table_data(self, table_name)`: Generate data for specific table
   - `apply_business_rules(self, data, table_name)`: Apply business rules
   - `inject_test_scenarios(self, data, table_name)`: Inject test scenarios
   - `save_to_csv(self, output_dir)`: Save generated data to CSV files ONLY

5. CRITICAL - Generation Order:
   - Use exactly: self.generation_order = {generation_order}
   - Do NOT change this order
   - This order ensures data consistency

6. Dependencies to use:
   - pandas for data manipulation
   - faker for realistic data generation
   - numpy for statistical distributions
   - datetime for date/time handling
   - random for randomization
   - uuid for unique identifiers

7. Output Format - IMPORTANT:
   - Generate ONLY CSV files for each table
   - Save CSV files to: output_dir + '/data/table_name.csv'

8. File Naming:
   - Use exact table names: customer_info.csv, credit_card_accounts.csv, etc.
   - Save to: os.path.join(output_dir, 'data', 'table_name.csv')

9. IMPORTANT CONSTRAINTS:
   - Only save main CSV files
   - NO validation reports or additional files

10. DATE/TIME HANDLING - CRITICAL:
    - Use random.randint() for date ranges, NEVER random.randrange()
    - Ensure start < end in all date ranges
    - Use datetime.timedelta for date arithmetic
    - Use try-catch blocks around date generation
    - For dates: datetime.now() - timedelta(days=random.randint(1, 365))

11. PANDAS SERIES HANDLING - CRITICAL:
     - NEVER use 'if value in series' - use .isin() or .any() instead
     - For row access: row['column'].iloc[0] or row['column'].item()
     - Always convert Series to scalar before comparisons

12. DATA TYPE VALIDATION - CRITICAL:
     - Check datetime before using .dt: pd.api.types.is_datetime64_any_dtype()
     - Convert strings to datetime: pd.to_datetime(column, errors='coerce')
     - Never use .dt on non-datetime columns

13. ERROR HANDLING - CRITICAL:
     - Wrap operations in try-catch
     - Use fallback values for all operations
     - If logging errors: except Exception as e:
     - If silent fallback: except Exception:

14. DATA VALIDATION - CRITICAL:
     - Replace NaN: df.fillna('')
     - Replace infinite: df.replace([np.inf, -np.inf], 0)
     - Validate dates: pd.to_datetime() with errors='coerce'

15. CODE STRUCTURE - CRITICAL:
     - Generate data first, then create DataFrame
     - Always return a value from methods
     - Check if data exists before using it
     - Use defensive programming - assume data might be invalid

16. VARIABLE SCOPE & METHOD STRUCTURE - CRITICAL:
    - Ensure all variables are defined before use
    - Check method parameters are properly passed
    - Always return a value from methods
    - Never reference undefined variables in exception handlers

Create a complete, runnable Python script that can be executed directly. The script should be well-documented, handle errors gracefully, and produce realistic synthetic data that meets all the specified requirements.

Return only the Python code, no explanations or markdown formatting.
"""
        return prompt
    
    def call_openai_for_code(self, prompt: str) -> str:
        """Call OpenAI API to generate the synthetic data generation code."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert Python developer specializing in synthetic data generation. Write clean, efficient, and well-documented Python code that can be executed directly.

CRITICAL CODING RULES:
1. ALWAYS use random.randint() instead of random.randrange() for date/time generation
2. ALWAYS ensure start < end in date ranges: random.randint(start, end) where start < end
3. For timestamps, use: random.randint(int(time.time()) - days*24*3600, int(time.time()))
4. For dates, use: random.randint(start_timestamp, end_timestamp) where start_timestamp < end_timestamp
5. NEVER use negative step values in randrange()
6. ALWAYS validate date ranges before using them
7. Use datetime.timedelta for date arithmetic, not direct timestamp subtraction
8. For date generation, prefer: datetime.now() - timedelta(days=random.randint(1, 365))
9. Handle edge cases where date ranges might be invalid
10. Use try-catch blocks around date generation to handle errors gracefully
11. ALWAYS convert numpy types to Python types: int(numpy_value) before using with timedelta
12. Use int() to convert any numpy.int32, numpy.int64 to regular Python int
13. For timedelta: timedelta(days=int(numpy_value)) or timedelta(days=int(random.randint(1, 365)))

ERROR PREVENTION:
- Check all random number generation for valid ranges
- Validate all date/time calculations
- Use safe defaults for edge cases
- Implement proper error handling for date operations"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=32000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return None
    
    def save_generated_code(self, code: str) -> str:
        """Save the generated code to a file in the synthetic_data/scripts directory."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.synthetic_data_dir, "scripts", f"synthetic_data_generator_{timestamp}.py")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            logger.info(f"Generated code saved to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving generated code: {str(e)}")
            return None
    
    def execute_generated_code(self, code_file: str, config: Dict[str, Any]) -> bool:
        """Execute the generated synthetic data generation code."""
        try:
            # Load the generated module
            spec = importlib.util.spec_from_file_location("generated_generator", code_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Add output directory to config
            config['output_dir'] = self.synthetic_data_dir
            
            # Create generator instance and run
            generator = module.SyntheticDataGenerator(config)
            generator.generate_all_data()
            generator.save_to_csv(self.synthetic_data_dir)
            
            logger.info("Synthetic data generation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing generated code: {str(e)}")
            return False
    
    def run_generation(self, config: Dict[str, Any] = None) -> bool:
        """Main method to run the synthetic data generation process."""
        print(f"\n🤖 AI-Powered Synthetic Data Generation Engine")
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
        
        logger.info(f"🚀 Initializing intelligent synthetic data generation for run: {self.run_id}")
        
        # Merge run configuration with provided config
        if config is None:
            config = {}
        
        # Use run configuration to enhance the config
        if self.run_config:
            # Set product-specific defaults
            if self.run_config.get('product_type') == 'synthetic-data-generation':
                config.setdefault('volume_percentage', 0.1)
                config.setdefault('scenario_mix', {
                    "positive": 0.7,
                    "negative": 0.2,
                    "edge_case": 0.1
                })
                config.setdefault('output_format', 'csv')
                config.setdefault('seed', 42)
                
                # Product-specific volume overrides
                config.setdefault('volume_overrides', {
                    "credit_card_transactions": 1000,
                    "imobile_user_session": 5000
                })
                
                logger.info(f"🎯 Using synthetic data generation configuration")
            else:
                logger.info(f"🎯 Using custom product configuration: {self.run_config.get('product_type')}")
        
        # Default configuration if no run config
        if not config:
            config = {
                "volume_percentage": 0.1,  # Generate 10% of recommended volumes
                "volume_overrides": {
                    "credit_card_transactions": 1000,  # Override to 1000 transactions
                    "imobile_user_session": 5000       # Override to 5000 sessions
                },
                "scenario_mix": {
                    "positive": 0.7,
                    "negative": 0.2,
                    "edge_case": 0.1
                },
                "output_format": "csv",
                "seed": 42  # For reproducible generation
            }
        
        logger.info(f"⚙️ Configuration loaded: {config.get('volume_percentage', 0.1)*100}% volume, {config.get('scenario_mix', {})} scenario mix")
        
        # Step 1: Load analysis results
        print("\n📋 STEP 1: Loading Schema Analysis")
        logger.info("🔍 Loading AI-generated schema analysis results...")
        analysis_results = self.load_analysis_results()
        if not analysis_results:
            logger.error("❌ Failed to load analysis results")
            return False
        
        logger.info("✅ Schema analysis loaded successfully")
        print(f"   📊 Tables to generate: {len(analysis_results.get('tables', []))}")
        
        # Step 2: Load original schemas (use run config to determine source)
        print("\n📋 STEP 2: Schema Structure Analysis")
        logger.info("🔍 Loading original schema definitions...")
        
        # Try to load from run-specific input data first
        original_schemas = {}
        if self.run_config and self.run_config.get('folder_structure', {}).get('target_subdir'):
            target_subdir = self.run_config['folder_structure']['target_subdir']
            run_input_dir = os.path.join(self.input_data_dir, target_subdir)
            logger.info(f"🔍 Looking for schemas in run-specific directory: {run_input_dir}")
            
            if os.path.exists(run_input_dir):
                original_schemas = self.load_schemas_from_directory(run_input_dir)
                if original_schemas:
                    logger.info(f"✅ Loaded {len(original_schemas)} schemas from run directory")
        
        # Fallback to original input_schemas if no schemas found in run directory
        if not original_schemas:
            logger.info("🔍 Fallback: Loading from original input_schemas directory")
            # Only load schemas for tables that have input data in this run
            available_tables = set()
            if analysis_results and 'tables' in analysis_results:
                available_tables = {table['table_name'] for table in analysis_results['tables']}
            
            if available_tables:
                logger.info(f"🔍 Loading schemas only for available tables: {list(available_tables)}")
                original_schemas = self.load_schemas_for_tables(available_tables)
            else:
                logger.info("�� No tables found in analysis, loading all schemas")
                original_schemas = self.load_original_schemas()
        
        if not original_schemas:
            logger.error("❌ Failed to load original schemas")
            return False
        
        logger.info(f"✅ Loaded {len(original_schemas)} schema definitions")
        
        # Step 3: Build dependency graph
        print("\n🧠 STEP 3: Dependency Analysis")
        logger.info("🔗 Analyzing table dependencies and relationships...")
        dependencies = self.build_dependency_graph(analysis_results)
        generation_order = self.get_generation_order(dependencies)
        
        logger.info(f"✅ Dependency graph built - Generation order: {generation_order}")
        print(f"   🔄 Generation sequence: {' → '.join(generation_order)}")
        
        # Step 4: Generate code using LLM
        print("\n🤖 STEP 4: AI Code Generation")
        logger.info("🚀 Engaging OpenAI GPT-4 for intelligent code generation...")
        print("   🔄 AI is generating sophisticated data generation logic...")
        prompt = self.generate_code_prompt(analysis_results, original_schemas, config, generation_order)
        code = self.call_openai_for_code(prompt)
        
        if not code:
            logger.error("❌ Failed to generate code")
            return False
        
        logger.info("✅ AI code generation completed")
        print("   ✅ Intelligent data generation code created")
        
        # Step 5: Save generated code
        print("\n💾 STEP 5: Code Persistence")
        logger.info("💾 Saving AI-generated code to scripts directory...")
        code_file = self.save_generated_code(code)
        if not code_file:
            logger.error("❌ Failed to save generated code")
            return False
        
        logger.info(f"✅ Code saved to: {code_file}")
        
        # Step 6: Execute the generated code
        print("\n⚡ STEP 6: Data Generation Execution")
        logger.info("🚀 Executing AI-generated synthetic data generation...")
        print("   🔄 Generating realistic synthetic data with business logic...")
        success = self.execute_generated_code(code_file, config)
        
        if success:
            logger.info("🎉 Synthetic data generation completed successfully")
            print(f"   ✅ Data generation completed successfully")
            print(f"   📁 Generated data saved to: {os.path.join(self.synthetic_data_dir, 'data')}")
            print(f"   📁 Generated code saved to: {code_file}")
        else:
            logger.error("❌ Synthetic data generation failed")
        
        return success

def main():
    """Main function to run the synthetic data generator agent."""
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
        print("\n🔧 Synthetic Data Generator Agent")
        print("="*50)
        print("Select a run ID that has schema analysis completed:")
        
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
        agent = SyntheticDataGeneratorAgent(OPENAI_API_KEY, run_id=run_id)
        
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
        
        # Run the generation
        success = agent.run_generation(config=config)
        
        if success:
            print("\n" + "="*50)
            print("SYNTHETIC DATA GENERATION COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"Run ID: {agent.run_id}")
            print("Generated files:")
            print(f"- Data files: {os.path.join(agent.synthetic_data_dir, 'data')}/")
            print(f"- Generated code: {os.path.join(agent.synthetic_data_dir, 'scripts')}/generated_data_generator.py")
        else:
            print("Synthetic data generation failed")
            
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 