import os
import sys
import json
import pandas as pd
from openai import OpenAI
from config import OPENAI_API_KEY
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from run_id_manager import generate_run_id, list_runs, get_run_info

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SchemaAnalyzerAgent:
    def __init__(self, api_key: str, run_id: str = None, mode: str = "full"):
        """Initialize the Schema Analyzer Agent with OpenAI client.
        
        Args:
            api_key: OpenAI API key
            run_id: Unique run ID (auto-generated if None)
            mode: Analysis mode - "full" (with test scenarios and business logic) or "schema_only" (schema analysis only)
        """
        self.client = OpenAI(api_key=api_key)
        self.run_id = run_id or generate_run_id()
        
        # Define folder structure FIRST
        self.base_dir = "runs"
        self.run_dir = os.path.join(self.base_dir, self.run_id)
        self.input_data_dir = os.path.join(self.run_dir, "input_data")
        self.schema_dir = os.path.join(self.run_dir, "schema")
        self.synthetic_data_dir = os.path.join(self.run_dir, "synthetic_data")
        self.validation_dir = os.path.join(self.run_dir, "validation")
        
        # Create directory structure
        self.create_directory_structure()
        
        # NOW try to read run configuration if run_id is provided
        self.run_config = None
        if self.run_id:
            self.run_config = self.load_run_config()
            if self.run_config:
                # Use configuration from run config file
                self.mode = self.run_config.get("analysis_mode", mode)
                logger.info(f"Loaded run configuration for {self.run_id}, using mode: {self.mode}")
            else:
                # Fallback to provided mode
                self.mode = mode
                logger.info(f"No run configuration found for {self.run_id}, using provided mode: {self.mode}")
        else:
            self.mode = mode
            logger.info(f"Using provided mode: {self.mode}")
        
        # Copy input data to run folder
        self.copy_input_data()
    
    def load_run_config(self) -> dict:
        """Load run configuration from the run's config file."""
        try:
            config_file_path = os.path.join(self.run_dir, "run_config.json")
            if os.path.exists(config_file_path):
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Successfully loaded run configuration from {config_file_path}")
                return config
            else:
                logger.info(f"No run configuration file found at {config_file_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading run configuration: {str(e)}")
            return None
    
    def ensure_working_directory(self):
        """Ensure the agent is working in the correct run directory."""
        try:
            # Get absolute paths
            run_dir_abs = os.path.abspath(self.run_dir)
            current_dir = os.getcwd()
            
            logger.info(f"Current working directory: {current_dir}")
            logger.info(f"Target run directory: {run_dir_abs}")
            
            # Change to run directory if we're not already there
            if current_dir != run_dir_abs:
                logger.info(f"Changing working directory from {current_dir} to {run_dir_abs}")
                os.chdir(run_dir_abs)
                logger.info(f"Working directory changed to: {os.getcwd()}")
            else:
                logger.info("Already in correct run directory")
                
        except Exception as e:
            logger.error(f"Error changing working directory: {str(e)}")
            # Continue with current directory if change fails
    
    def create_directory_structure(self):
        """Create the directory structure for this run."""
        try:
            # Ensure we're working with absolute paths
            run_dir_abs = os.path.abspath(self.run_dir)
            input_data_dir_abs = os.path.abspath(self.input_data_dir)
            schema_dir_abs = os.path.abspath(self.schema_dir)
            synthetic_data_dir_abs = os.path.abspath(self.synthetic_data_dir)
            validation_dir_abs = os.path.abspath(self.validation_dir)
            
            directories = [
                run_dir_abs,
                input_data_dir_abs,
                os.path.join(input_data_dir_abs, "schema"),        # For schema files
                os.path.join(input_data_dir_abs, "data"),          # For input data files
                schema_dir_abs,
                synthetic_data_dir_abs,
                os.path.join(synthetic_data_dir_abs, "data"),      # For CSV files
                os.path.join(synthetic_data_dir_abs, "scripts"),   # For Python files
                validation_dir_abs,
                os.path.join(validation_dir_abs, "reports"),       # For JSON/TXT reports
                os.path.join(validation_dir_abs, "scripts")        # For Python files
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
                
        except Exception as e:
            logger.error(f"Error creating directory structure: {str(e)}")
            raise
    
    def copy_input_data(self):
        """Copy input files to the run's input_data directory based on mode."""
        try:
            # Check if the run folder already contains uploaded data
            # Use absolute paths to avoid working directory confusion
            run_input_data_dir = os.path.abspath(os.path.join(self.base_dir, self.run_id, "input_data"))
            has_run_data = os.path.exists(run_input_data_dir) and len(os.listdir(run_input_data_dir)) > 0
            
            if has_run_data:
                logger.info(f"Run {self.run_id} already contains uploaded data in {run_input_data_dir}")
                # No need to copy, data is already in the right place
                return
            
            # Fallback: Copy from root directories (for backward compatibility)
            schema_source_dir = os.path.abspath("input_schemas")
            
            if not os.path.exists(schema_source_dir):
                logger.warning(f"Input schemas directory {schema_source_dir} not found")
                return
            
            if self.mode == "full":
                # Full mode: Copy schema files to input_data/schema
                schema_dest_dir = os.path.join(self.input_data_dir, "schema")
                os.makedirs(schema_dest_dir, exist_ok=True)
                
                copied_files = []
                for filename in os.listdir(schema_source_dir):
                    if filename.endswith('.csv'):
                        source_path = os.path.join(schema_source_dir, filename)
                        dest_path = os.path.join(schema_dest_dir, filename)
                        
                        # Copy the file
                        import shutil
                        shutil.copy2(source_path, dest_path)
                        copied_files.append(filename)
                        logger.info(f"Copied schema file: {filename}")
                
                if copied_files:
                    logger.info(f"Successfully copied {len(copied_files)} schema files to run {self.run_id}/input_data/schema")
                else:
                    logger.warning("No CSV files found in input_schemas directory")
                    
            elif self.mode == "schema_only":
                # Schema-only mode: Copy schema files to input_data/schema AND copy input data to input_data/data
                schema_dest_dir = os.path.join(self.input_data_dir, "schema")
                data_dest_dir = os.path.join(self.input_data_dir, "data")
                os.makedirs(schema_dest_dir, exist_ok=True)
                os.makedirs(data_dest_dir, exist_ok=True)
                
                # Copy schema files
                schema_files = []
                for filename in os.listdir(schema_source_dir):
                    if filename.endswith('.csv'):
                        source_path = os.path.join(schema_source_dir, filename)
                        dest_path = os.path.join(schema_dest_dir, filename)
                        
                        import shutil
                        shutil.copy2(source_path, dest_path)
                        schema_files.append(filename)
                        logger.info(f"Copied schema file: {filename}")
                
                # Copy input data files (assuming they exist in a separate directory)
                input_data_source_dir = "input_data"  # You might need to adjust this path
                if os.path.exists(input_data_source_dir):
                    data_files = []
                    for filename in os.listdir(input_data_source_dir):
                        if filename.endswith('.csv'):
                            source_path = os.path.join(input_data_source_dir, filename)
                            dest_path = os.path.join(data_dest_dir, filename)
                            
                            import shutil
                            shutil.copy2(source_path, dest_path)
                            data_files.append(filename)
                            logger.info(f"Copied input data file: {filename}")
                    
                    logger.info(f"Successfully copied {len(schema_files)} schema files and {len(data_files)} data files to run {self.run_id}")
                else:
                    logger.info(f"Successfully copied {len(schema_files)} schema files to run {self.run_id} (no input data directory found)")
                
        except Exception as e:
            logger.error(f"Error copying input data: {str(e)}")
        
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
    
    def analyze_schemas(self) -> List[Dict[str, Any]]:
        """Read and analyze all CSV schema files."""
        schemas = []
        
        # First, look for files in the run folder (from uploads) based on mode
        # Use absolute paths to avoid working directory confusion
        run_input_data_dir = os.path.abspath(os.path.join(self.base_dir, self.run_id, "input_data"))
        if os.path.exists(run_input_data_dir):
            logger.info(f"Looking for schema files in run folder: {run_input_data_dir}")
            
            # Use run configuration if available, otherwise determine from mode
            if self.run_config and "folder_structure" in self.run_config:
                target_subdir = self.run_config["folder_structure"]["target_subdir"]
                # Convert relative path to absolute
                if target_subdir.startswith("runs/"):
                    target_subdir = os.path.abspath(target_subdir)
                else:
                    target_subdir = os.path.abspath(os.path.join(self.base_dir, self.run_id, "input_data", target_subdir.split("/")[-1]))
                folder_purpose = f"files from {self.run_config.get('source_type', 'unknown')} for {self.run_config.get('product_type', 'unknown')}"
                logger.info(f"Using folder structure from run configuration: {target_subdir}")
            else:
                # Fallback: Determine which subdirectory to look in based on mode
                if self.mode == "full":
                    # Full mode: Look in input_data/data (both synthetic data generation and functional test scenarios)
                    target_subdir = os.path.join(run_input_data_dir, "data")
                    folder_purpose = "data files for comprehensive analysis"
                else:
                    # Schema-only mode: Look in input_data/data (for functional test scenarios)
                    target_subdir = os.path.join(run_input_data_dir, "data")
                    folder_purpose = "data files for functional test scenarios"
            
            if os.path.exists(target_subdir):
                logger.info(f"Looking for files in {target_subdir} ({folder_purpose})")
                for filename in os.listdir(target_subdir):
                    if filename.endswith('.csv'):
                        file_path = os.path.join(target_subdir, filename)
                        schema = self.read_csv_schema(file_path)
                        if schema:
                            schemas.append(schema)
                            logger.info(f"Successfully read schema for {filename} from run folder {target_subdir}")
                
                if schemas:
                    logger.info(f"Found {len(schemas)} schema files in run folder {target_subdir}")
                    return schemas
            else:
                logger.info(f"Target subdirectory {target_subdir} not found, checking root input_data directory")
                # Fallback: check the root input_data directory
                for filename in os.listdir(run_input_data_dir):
                    if filename.endswith('.csv'):
                        file_path = os.path.join(run_input_data_dir, filename)
                        schema = self.read_csv_schema(file_path)
                        if schema:
                            schemas.append(schema)
                            logger.info(f"Successfully read schema for {filename} from run folder root input_data")
                
                if schemas:
                    logger.info(f"Found {len(schemas)} schema files in run folder root input_data")
                    return schemas
        
        # Fallback: Look for schema files in the original schema directory (for backward compatibility)
        schema_source_dir = os.path.abspath("input_schemas")
        
        if not os.path.exists(schema_source_dir):
            logger.error(f"Input schemas directory {schema_source_dir} not found")
            return schemas
        
        logger.info(f"Looking for schema files in root directory: {schema_source_dir}")
        for filename in os.listdir(schema_source_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(schema_source_dir, filename)
                schema = self.read_csv_schema(file_path)
                if schema:
                    schemas.append(schema)
                    logger.info(f"Successfully read schema for {filename} from root directory")
        
        return schemas
    
    def generate_analysis_prompt(self, schemas: List[Dict[str, Any]]) -> str:
        """Generate the prompt for OpenAI to analyze schemas and identify primary keys."""
        
        if self.mode == "full":
            # Full mode: Generate test scenarios and business logic
            prompt = f"""
You are a database schema analyst specializing in financial systems. Analyze the following CSV schemas and provide a comprehensive analysis.

SCHEMAS TO ANALYZE:
{json.dumps(schemas, indent=2)}

TASK: Analyze each table and provide:
1. PRIMARY KEY IDENTIFICATION: Identify the most likely primary key for each table based on uniqueness and business logic
2. BUSINESS RULES ANALYSIS: Identify business rules and constraints that should be enforced
3. TEST SCENARIOS: Generate EXACTLY 3-5 UNIQUE test scenarios per table

CRITICAL REQUIREMENTS:
- Generate EXACTLY 3-5 UNIQUE business rules and 3-5 UNIQUE test scenarios TOTAL
- DISTRIBUTE EVENLY across different tables - don't concentrate on one table
- EACH rule and scenario must be UNIQUE - no duplicate names, descriptions, or logic
- Focus on realistic financial domain scenarios
- Consider relationships between tables (foreign keys)
- Include both positive and negative test cases
- Provide specific validation rules and constraints
- Consider data types and format requirements
- AVOID DUPLICATES: Each business rule and test scenario must be unique and different from others

DISTRIBUTION GUIDELINES:
- If you have 3+ tables, generate 1-2 rules/scenarios per table
- If you have 2 tables, generate 2-3 rules/scenarios per table  
- If you have 1 table, generate 3-5 rules/scenarios for that table
- Ensure NO DUPLICATES across all tables

OUTPUT FORMAT: Return a JSON object with the following structure:
{{
    "tables": [
        {{
            "table_name": "string",
            "primary_key": "string",
            "business_rules": [
                {{
                    "rule_name": "unique_rule_name",
                    "description": "unique_description",
                    "validation_logic": "string",
                    "error_message": "string",
                    "rule_type": "business_logic|uniqueness|referential|range|enumeration",
                    "severity": "CRITICAL|HIGH|MEDIUM|LOW"
                }}
            ],
            "test_scenarios": [
                {{
                    "scenario_name": "unique_scenario_name",
                    "description": "unique_description",
                    "test_type": "positive|negative|edge_case",
                    "business_logic": "string",
                    "expected_behavior": "string",
                    "data_requirements": {{
                        "field_name": "string",
                        "constraints": "string",
                        "sample_values": ["string"]
                    }},
                    "priority": "CRITICAL|HIGH|MEDIUM|LOW"
                }}
            ],
            "data_generation_rules": [
                {{
                    "field_name": "string",
                    "generation_logic": "string",
                    "constraints": "string",
                    "dependencies": ["string"]
                }}
            ]
        }}
    ],
    "cross_table_relationships": [
        {{
            "from_table": "string",
            "to_table": "string",
            "relationship_type": "string",
            "description": "string",
            "foreign_key": "string"
        }}
    ],
    "synthetic_data_requirements": {{
        "volume_recommendations": {{
            "table_name": "string",
            "recommended_count": "number",
            "reasoning": "string"
        }},
        "data_distribution": {{
            "table_name": "string",
            "field_name": "string",
            "distribution_type": "string",
            "parameters": {{}}
        }}
    }}
}}

IMPORTANT: 
- Return EXACTLY 3-5 UNIQUE business rules and 3-5 UNIQUE test scenarios TOTAL
- Each rule and scenario must be UNIQUE and different from others
- Distribute across different tables evenly
- Return ONLY the JSON object, no additional text or explanations

Analyze the schemas thoroughly and provide detailed, actionable insights for synthetic data generation.
"""
        else:
            # Schema-only mode: Just analyze schema structure
            prompt = f"""
You are a database schema analyst specializing in financial systems. Analyze the following CSV schemas and provide schema analysis only.

SCHEMAS TO ANALYZE:
{json.dumps(schemas, indent=2)}

TASK: Analyze each table and provide:
1. PRIMARY KEY IDENTIFICATION: Identify the most likely primary key for each table based on uniqueness and business logic
2. SCHEMA STRUCTURE ANALYSIS: Analyze column types, relationships, and data patterns
3. CROSS-TABLE RELATIONSHIPS: Identify potential foreign key relationships

REQUIREMENTS:
- Focus on schema structure and relationships
- Identify data types and constraints
- Map relationships between tables
- Do NOT generate business rules or test scenarios

OUTPUT FORMAT: Return a JSON object with the following structure:
{{
    "tables": [
        {{
            "table_name": "string",
            "primary_key": "string",
            "columns": [
                {{
                    "name": "string",
                    "data_type": "string",
                    "description": "string",
                    "sample_values": "string"
                }}
            ],
            "schema_analysis": {{
                "data_patterns": ["string"],
                "constraints": ["string"],
                "relationships": ["string"]
            }}
        }}
    ],
    "cross_table_relationships": [
        {{
            "from_table": "string",
            "to_table": "string",
            "relationship_type": "string",
            "foreign_key": "string",
            "description": "string"
        }}
    ],
    "schema_summary": {{
        "total_tables": "number",
        "total_columns": "number",
        "primary_keys": ["string"],
        "foreign_keys": ["string"]
    }}
}}

Analyze the schemas thoroughly and provide detailed schema structure insights.
"""
        
        return prompt
    
    def call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API to analyze schemas."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert database analyst and test data engineer specializing in financial systems. Provide detailed, accurate analysis with practical recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=10000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Try to extract JSON from the response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end == -1:
                    json_end = len(content)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content.strip()
            
            # Clean up the JSON string - remove any trailing text after the JSON
            # Find the last complete JSON object by counting braces
            brace_count = 0
            last_complete_pos = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(json_str):
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            last_complete_pos = i + 1
                            break
            
            if last_complete_pos > 0:
                json_str = json_str[:last_complete_pos]
            
            # Additional cleanup: remove any trailing text that might be after the JSON
            # Look for common patterns that indicate the JSON has ended
            json_end_markers = [
                "```",
                "**Key Notes:**",
                "Note:",
                "Summary:",
                "Conclusion:",
                "The JSON response",
                "This analysis"
            ]
            
            for marker in json_end_markers:
                marker_pos = json_str.find(marker)
                if marker_pos != -1:
                    json_str = json_str[:marker_pos].strip()
                    break
            
            # Try to parse the JSON
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                # Try a more aggressive cleanup approach
                logger.warning(f"Initial JSON parsing failed: {e}")
                
                # Try to find the JSON object more precisely
                # Look for the start of the JSON object
                json_start = json_str.find('{')
                if json_start != -1:
                    # Find the matching closing brace
                    brace_count = 0
                    json_end = -1
                    in_string = False
                    escape_next = False
                    
                    for i in range(json_start, len(json_str)):
                        char = json_str[i]
                        
                        if escape_next:
                            escape_next = False
                            continue
                        
                        if char == '\\':
                            escape_next = True
                            continue
                        
                        if char == '"' and not escape_next:
                            in_string = not in_string
                            continue
                        
                        if not in_string:
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    json_end = i + 1
                                    break
                    
                    if json_end > json_start:
                        cleaned_json = json_str[json_start:json_end]
                        try:
                            return json.loads(cleaned_json)
                        except json.JSONDecodeError as e2:
                            logger.error(f"Second attempt at JSON parsing failed: {e2}")
                
                # If all parsing attempts fail, save the raw response and return error
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response length: {len(content)}")
                logger.error(f"Raw response preview: {content[:500]}...")
                
                # Try to save the raw response for manual inspection
                try:
                    raw_response_file = self.safe_file_path("raw_openai_response.json")
                    logger.info(f"Saving raw response to: {raw_response_file}")
                    with open(raw_response_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    logger.info("Raw response saved to raw_openai_response.json for manual inspection")
                except Exception as save_error:
                    logger.error(f"Failed to save raw response: {save_error}")
                
                return {"error": "Failed to parse OpenAI response", "raw_response": content}
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return {"error": f"API call failed: {str(e)}"}
    
    def save_analysis_results(self, analysis: Dict[str, Any]):
        """Save analysis results to JSON file in the schema directory."""
        try:
            # Use safe file path helper to ensure file is saved in the correct location
            output_file = self.safe_file_path("schema_analysis_results.json", "schema")
            
            # Log the target file path for debugging
            logger.info(f"Saving analysis results to: {output_file}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"Analysis results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}")
    
    def post_process_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process the AI-generated analysis to ensure quality and remove duplicates."""
        try:
            logger.info("Starting post-processing of AI-generated analysis...")
            
            if "tables" not in analysis:
                logger.warning("No tables found in analysis, skipping post-processing")
                return analysis
            
            # Process each table
            for table in analysis["tables"]:
                if "business_rules" in table:
                    table["business_rules"] = self.deduplicate_business_rules(table["business_rules"])
                
                if "test_scenarios" in table:
                    table["test_scenarios"] = self.deduplicate_test_scenarios(table["test_scenarios"])
            
            # Ensure minimum count across all tables
            analysis = self.ensure_minimum_counts(analysis)
            
            logger.info("Post-processing completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error during post-processing: {str(e)}")
            return analysis
    
    def deduplicate_business_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate business rules based on name and description."""
        try:
            seen_rules = set()
            unique_rules = []
            
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                    
                rule_name = rule.get('rule_name', '')
                description = rule.get('description', '')
                
                if not rule_name or not description:
                    continue
                
                # Create a unique key for deduplication
                rule_key = f"{rule_name}_{description}"
                
                if rule_key not in seen_rules:
                    seen_rules.add(rule_key)
                    unique_rules.append(rule)
                else:
                    logger.info(f"Removing duplicate business rule: {rule_name}")
            
            logger.info(f"Deduplicated business rules: {len(rules)} -> {len(unique_rules)}")
            return unique_rules
            
        except Exception as e:
            logger.error(f"Error deduplicating business rules: {str(e)}")
            return rules
    
    def deduplicate_test_scenarios(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate test scenarios based on name and description."""
        try:
            seen_scenarios = set()
            unique_scenarios = []
            
            for scenario in scenarios:
                if not isinstance(scenario, dict):
                    continue
                    
                scenario_name = scenario.get('scenario_name', '')
                description = scenario.get('description', '')
                
                if not scenario_name or not description:
                    continue
                
                # Create a unique key for deduplication
                scenario_key = f"{scenario_name}_{description}"
                
                if scenario_key not in seen_scenarios:
                    seen_scenarios.add(scenario_key)
                    unique_scenarios.append(scenario)
                else:
                    logger.info(f"Removing duplicate test scenario: {scenario_name}")
            
            logger.info(f"Deduplicated test scenarios: {len(scenarios)} -> {len(unique_scenarios)}")
            return unique_scenarios
            
        except Exception as e:
            logger.error(f"Error deduplicating test scenarios: {str(e)}")
            return scenarios
    
    def ensure_minimum_counts(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure minimum counts of business rules and test scenarios across all tables."""
        try:
            if "tables" not in analysis:
                return analysis
            
            total_rules = 0
            total_scenarios = 0
            
            # Count current totals
            for table in analysis["tables"]:
                if "business_rules" in table:
                    total_rules += len(table["business_rules"])
                if "test_scenarios" in table:
                    total_scenarios += len(table["test_scenarios"])
            
            logger.info(f"Current totals: {total_rules} business rules, {total_scenarios} test scenarios")
            
            # If we have enough, return as is
            if total_rules >= 3 and total_scenarios >= 3:
                logger.info("Minimum counts already met")
                return analysis
            
            # Generate additional items if needed
            if total_rules < 3:
                logger.info(f"Generating {3 - total_rules} additional business rules")
                analysis = self.add_additional_business_rules(analysis, 3 - total_rules)
            
            if total_scenarios < 3:
                logger.info(f"Generating {3 - total_scenarios} additional test scenarios")
                analysis = self.add_additional_test_scenarios(analysis, 3 - total_scenarios)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error ensuring minimum counts: {str(e)}")
            return analysis
    
    def add_additional_business_rules(self, analysis: Dict[str, Any], count_needed: int) -> Dict[str, Any]:
        """Add additional business rules to meet minimum count."""
        try:
            # Simple template-based business rules
            additional_rules = [
                {
                    "rule_name": "Data Integrity Check",
                    "description": "Ensure critical fields are not null",
                    "validation_logic": "critical_field IS NOT NULL",
                    "error_message": "Critical field cannot be null",
                    "rule_type": "business_logic",
                    "severity": "HIGH"
                },
                {
                    "rule_name": "Range Validation",
                    "description": "Ensure numeric values are within valid range",
                    "validation_logic": "value >= min_value AND value <= max_value",
                    "error_message": "Value out of valid range",
                    "rule_type": "range",
                    "severity": "MEDIUM"
                }
            ]
            
            # Add to first table that has business_rules
            for table in analysis["tables"]:
                if "business_rules" in table:
                    for i in range(min(count_needed, len(additional_rules))):
                        rule = additional_rules[i].copy()
                        rule["rule_name"] = f"{rule['rule_name']}_{i+1}"
                        table["business_rules"].append(rule)
                    break
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error adding additional business rules: {str(e)}")
            return analysis
    
    def add_additional_test_scenarios(self, analysis: Dict[str, Any], count_needed: int) -> Dict[str, Any]:
        """Add additional test scenarios to meet minimum count."""
        try:
            # Simple template-based test scenarios
            additional_scenarios = [
                {
                    "scenario_name": "Positive Test Case",
                    "description": "Test valid data scenario",
                    "test_type": "positive",
                    "business_logic": "valid_data = true",
                    "expected_behavior": "System accepts valid data",
                    "data_requirements": "Valid test data",
                    "priority": "MEDIUM"
                },
                {
                    "scenario_name": "Negative Test Case",
                    "description": "Test invalid data scenario",
                    "test_type": "negative",
                    "business_logic": "invalid_data = true",
                    "expected_behavior": "System rejects invalid data",
                    "data_requirements": "Invalid test data",
                    "priority": "HIGH"
                }
            ]
            
            # Add to first table that has test_scenarios
            for table in analysis["tables"]:
                if "test_scenarios" in table:
                    for i in range(min(count_needed, len(additional_scenarios))):
                        scenario = additional_scenarios[i].copy()
                        scenario["scenario_name"] = f"{scenario['scenario_name']}_{i+1}"
                        table["test_scenarios"].append(scenario)
                    break
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error adding additional test scenarios: {str(e)}")
            return analysis
    
    def integrate_business_logic(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate business rules and test scenarios from the library generator agent."""
        try:
            logger.info("Starting business logic integration...")
            
            # Check if business logic library exists
            library_dir = os.path.join(self.run_dir, "business_logic_library")
            if not os.path.exists(library_dir):
                logger.info("Business logic library not found, using AI-generated content")
                return analysis
            
            # Try to load business rules and test scenarios from CSV files
            business_rules = self.load_business_rules_from_library(library_dir)
            test_scenarios = self.load_test_scenarios_from_library(library_dir)
            
            if business_rules or test_scenarios:
                logger.info(f"Found {len(business_rules) if business_rules else 0} business rules and {len(test_scenarios) if test_scenarios else 0} test scenarios from library")
                
                # Integrate them into the analysis
                analysis = self.merge_business_logic(analysis, business_rules, test_scenarios)
                
                # Apply deduplication and ensure minimum counts
                analysis = self.post_process_analysis(analysis)
                
                logger.info("Business logic integration completed successfully")
            else:
                logger.info("No business logic found in library, using AI-generated content")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error during business logic integration: {str(e)}")
            return analysis
    
    def load_business_rules_from_library(self, library_dir: str) -> List[Dict[str, Any]]:
        """Load business rules from the library CSV file."""
        try:
            business_rules_file = os.path.join(library_dir, "business_rules.csv")
            if not os.path.exists(business_rules_file):
                return []
            
            import pandas as pd
            df = pd.read_csv(business_rules_file)
            
            business_rules = []
            for _, row in df.iterrows():
                rule = {
                    "table_name": row.get("table_name", ""),
                    "rule_name": row.get("rule_name", ""),
                    "rule_type": row.get("rule_type", "business_logic"),
                    "description": row.get("description", ""),
                    "validation_logic": row.get("validation_logic", ""),
                    "error_message": row.get("error_message", ""),
                    "severity": row.get("severity", "MEDIUM"),
                    "is_active": row.get("is_active", 1)
                }
                business_rules.append(rule)
            
            logger.info(f"Loaded {len(business_rules)} business rules from library")
            return business_rules
            
        except Exception as e:
            logger.error(f"Error loading business rules from library: {str(e)}")
            return []
    
    def load_test_scenarios_from_library(self, library_dir: str) -> List[Dict[str, Any]]:
        """Load test scenarios from the library CSV file."""
        try:
            test_scenarios_file = os.path.join(library_dir, "test_scenarios.csv")
            if not os.path.exists(test_scenarios_file):
                return []
            
            import pandas as pd
            df = pd.read_csv(test_scenarios_file)
            
            test_scenarios = []
            for _, row in df.iterrows():
                scenario = {
                    "table_name": row.get("table_name", ""),
                    "scenario_name": row.get("scenario_name", ""),
                    "scenario_type": row.get("scenario_type", "positive"),
                    "description": row.get("description", ""),
                    "test_conditions": row.get("test_conditions", ""),
                    "expected_behavior": row.get("expected_behavior", ""),
                    "data_requirements": row.get("data_requirements", ""),
                    "priority": row.get("priority", "MEDIUM"),
                    "is_active": row.get("is_active", 1)
                }
                test_scenarios.append(scenario)
            
            logger.info(f"Loaded {len(test_scenarios)} test scenarios from library")
            return test_scenarios
            
        except Exception as e:
            logger.error(f"Error loading test scenarios from library: {str(e)}")
            return []
    
    def merge_business_logic(self, analysis: Dict[str, Any], business_rules: List[Dict[str, Any]], test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge business rules and test scenarios into the analysis structure."""
        try:
            if "tables" not in analysis:
                return analysis
            
            # Group business rules and test scenarios by table
            rules_by_table = {}
            scenarios_by_table = {}
            
            for rule in business_rules:
                table_name = rule.get("table_name", "")
                if table_name not in rules_by_table:
                    rules_by_table[table_name] = []
                rules_by_table[table_name].append(rule)
            
            for scenario in test_scenarios:
                table_name = scenario.get("table_name", "")
                if table_name not in scenarios_by_table:
                    scenarios_by_table[table_name] = []
                scenarios_by_table[table_name].append(scenario)
            
            # Merge into analysis tables
            for table in analysis["tables"]:
                table_name = table.get("table_name", "")
                
                # Add business rules
                if table_name in rules_by_table:
                    if "business_rules" not in table:
                        table["business_rules"] = []
                    table["business_rules"].extend(rules_by_table[table_name])
                    logger.info(f"Added {len(rules_by_table[table_name])} business rules to {table_name}")
                
                # Add test scenarios
                if table_name in scenarios_by_table:
                    if "test_scenarios" not in table:
                        table["test_scenarios"] = []
                    table["test_scenarios"].extend(scenarios_by_table[table_name])
                    logger.info(f"Added {len(scenarios_by_table[table_name])} test scenarios to {table_name}")
            
            logger.info("Business logic merge completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error merging business logic: {str(e)}")
            return analysis
    
    def run_analysis(self) -> Dict[str, Any]:
        """Main method to run the complete schema analysis."""
        print(f"\n🧠 AI-Powered Schema Analysis Engine")
        print(f"📊 Run ID: {self.run_id} | Mode: {self.mode}")
        print("="*60)
        
        # Ensure we're working in the correct run directory
        self.ensure_working_directory()
        
        # Log current working directory and run directory for debugging
        current_dir = os.getcwd()
        logger.info(f"Current working directory: {current_dir}")
        logger.info(f"Run directory: {os.path.abspath(self.run_dir)}")
        
        logger.info(f"🤖 Initializing intelligent schema analysis for run: {self.run_id}")
        logger.info(f"🎯 Analysis mode: {self.mode} - {'Comprehensive analysis with business logic' if self.mode == 'full' else 'Schema structure analysis'}")
        
        # Step 1: Read and parse all CSV schemas
        print("\n📋 STEP 1: Schema Discovery & Parsing")
        logger.info("🔍 Scanning input schemas directory for CSV files...")
        schemas = self.analyze_schemas()
        if not schemas:
            logger.error("❌ No schemas found to analyze")
            return {"error": "No schemas found"}
        
        logger.info(f"✅ Discovered {len(schemas)} schema files")
        print(f"   📁 Found schemas: {', '.join([s['table_name'] for s in schemas])}")
        
        # Step 2: Generate analysis prompt
        print("\n🧠 STEP 2: AI Analysis Preparation")
        logger.info("🤖 Preparing intelligent analysis prompt with schema context...")
        prompt = self.generate_analysis_prompt(schemas)
        logger.info(f"📝 Generated comprehensive prompt ({len(prompt)} characters)")
        
        # Step 3: Call OpenAI API for analysis
        print("\n🤖 STEP 3: AI-Powered Schema Analysis")
        logger.info("🚀 Engaging OpenAI GPT-4 for intelligent schema analysis...")
        print("   🔄 AI is analyzing table structures, relationships, and business logic...")
        analysis = self.call_openai_api(prompt)
        
        if "error" in analysis:
            logger.error(f"❌ AI analysis failed: {analysis['error']}")
            return analysis
        
        logger.info("✅ AI analysis completed successfully")
        print("   ✅ AI analysis completed - insights extracted")
        
        # Step 3.5: Post-process results to ensure quality and remove duplicates
        print("\n🔧 STEP 3.5: Post-Processing & Quality Assurance")
        logger.info("🔧 Applying post-processing to ensure quality and remove duplicates...")
        analysis = self.post_process_analysis(analysis)
        logger.info("✅ Post-processing completed")
        print("   ✅ Quality assurance and deduplication applied")
        
        # Step 3.6: Integrate business rules and test scenarios from library generator
        print("\n🔗 STEP 3.6: Business Logic Integration")
        logger.info("🔗 Integrating business rules and test scenarios from library generator...")
        analysis = self.integrate_business_logic(analysis)
        logger.info("✅ Business logic integration completed")
        print("   ✅ Business rules and test scenarios integrated")
        
        # Step 4: Save results
        print("\n💾 STEP 4: Results Persistence")
        logger.info("💾 Persisting AI-generated analysis results...")
        self.save_analysis_results(analysis)
        
        logger.info("🎉 Schema analysis pipeline completed successfully")
        print("   📊 Analysis results saved to schema directory")
        
        return analysis
    
    def run_analysis_with_library_integration(self) -> Dict[str, Any]:
        """Run schema analysis with direct library integration (no AI API calls)."""
        print(f"\n🔗 Schema Analysis with Library Integration")
        print(f"📊 Run ID: {self.run_id} | Mode: {self.mode}")
        print("="*60)
        
        # Ensure we're working in the correct run directory
        self.ensure_working_directory()
        
        # Step 1: Read and parse all CSV schemas
        print("\n📋 STEP 1: Schema Discovery & Parsing")
        logger.info("🔍 Scanning input schemas directory for CSV files...")
        schemas = self.analyze_schemas()
        if not schemas:
            logger.error("❌ No schemas found to analyze")
            return {"error": "No schemas found"}
        
        logger.info(f"✅ Discovered {len(schemas)} schema files")
        print(f"   📁 Found schemas: {', '.join([s['table_name'] for s in schemas])}")
        
        # Step 2: Create basic schema structure
        print("\n🏗️  STEP 2: Schema Structure Creation")
        logger.info("🏗️  Creating basic schema structure...")
        analysis = self.create_basic_schema_structure(schemas)
        logger.info("✅ Basic schema structure created")
        
        # Step 3: Integrate business logic from library
        print("\n🔗 STEP 3: Business Logic Integration")
        logger.info("🔗 Integrating business rules and test scenarios from library...")
        analysis = self.integrate_business_logic(analysis)
        logger.info("✅ Business logic integration completed")
        print("   ✅ Business rules and test scenarios integrated")
        
        # Step 4: Post-process and ensure quality
        print("\n🔧 STEP 4: Quality Assurance")
        logger.info("🔧 Applying post-processing and quality checks...")
        analysis = self.post_process_analysis(analysis)
        logger.info("✅ Quality assurance completed")
        
        # Step 5: Save results
        print("\n💾 STEP 5: Results Persistence")
        logger.info("💾 Persisting integrated analysis results...")
        self.save_analysis_results(analysis)
        
        logger.info("🎉 Schema analysis with library integration completed successfully")
        print("   📊 Analysis results saved to schema directory")
        
        return analysis
    
    def create_basic_schema_structure(self, schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a basic schema structure from CSV schemas."""
        try:
            analysis = {
                "run_id": self.run_id,
                "generated_at": datetime.now().isoformat(),
                "mode": "library_integration",
                "tables": [],
                "cross_table_relationships": [
                    {
                        "from_table": "customer_info",
                        "to_table": "credit_card_accounts",
                        "relationship_type": "one_to_many",
                        "description": "Customer can have multiple credit card accounts",
                        "foreign_key": "customer_id"
                    },
                    {
                        "from_table": "credit_card_accounts",
                        "to_table": "credit_card_transactions",
                        "relationship_type": "one_to_many",
                        "description": "Account can have multiple transactions",
                        "foreign_key": "serial_number"
                    },
                    {
                        "from_table": "customer_info",
                        "to_table": "imobile_user_session",
                        "relationship_type": "one_to_many",
                        "description": "Customer can have multiple mobile sessions",
                        "foreign_key": "customer_id"
                    }
                ]
            }
            
            # Add table information from schemas
            for schema in schemas:
                table_info = {
                    "table_name": schema.get("table_name", ""),
                    "primary_key": schema.get("primary_key", ""),
                    "columns": schema.get("columns", []),
                    "business_rules": [],
                    "test_scenarios": [],
                    "data_generation_rules": []
                }
                analysis["tables"].append(table_info)
            
            logger.info(f"Created basic schema structure with {len(analysis['tables'])} tables")
            return analysis
            
        except Exception as e:
            logger.error(f"Error creating basic schema structure: {str(e)}")
            return {"error": f"Failed to create schema structure: {str(e)}"}

    def safe_file_path(self, filename: str, subdirectory: str = None) -> str:
        """Generate a safe file path within the run directory."""
        try:
            if subdirectory:
                # If subdirectory is specified, use it
                target_dir = os.path.abspath(os.path.join(self.run_dir, subdirectory))
            else:
                # Default to run directory
                target_dir = os.path.abspath(self.run_dir)
            
            # Ensure the target directory exists
            os.makedirs(target_dir, exist_ok=True)
            
            # Generate the full file path
            file_path = os.path.abspath(os.path.join(target_dir, filename))
            
            # Verify the file path is within the run directory (security check)
            run_dir_abs = os.path.abspath(self.run_dir)
            if not file_path.startswith(run_dir_abs):
                logger.error(f"Security check failed: File path {file_path} is outside run directory {run_dir_abs}")
                # Fallback to run directory
                file_path = os.path.abspath(os.path.join(run_dir_abs, filename))
            
            logger.info(f"Generated safe file path: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating safe file path: {str(e)}")
            # Fallback to run directory
            return os.path.abspath(os.path.join(self.run_dir, filename))

def main():
    """Main function to run the schema analyzer agent."""
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
        
        # Get user input for mode
        print("\n🔍 Schema Analyzer Agent")
        print("="*50)
        print("Select analysis mode:")
        print("1. Full analysis (with test scenarios and business logic) - Synthetic Data Generation")
        print("2. Schema-only analysis (structure only) - Functional Test Scenario Generation")
        
        while True:
            choice = input("Enter choice (1 or 2): ").strip()
            if choice == "1":
                mode = "full"
                break
            elif choice == "2":
                mode = "schema_only"
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
        
        # Ask if user wants to use existing run ID
        use_existing = input("Use existing run ID? (y/n): ").strip().lower()
        run_id = None
        
        if use_existing in ['y', 'yes']:
            if existing_runs:
                print(f"Available runs: {', '.join(existing_runs)}")
                run_id = input("Enter run ID: ").strip()
                if not run_id or not run_id.isdigit():
                    print("Invalid run ID. Generating new run ID.")
                    run_id = None
            else:
                print("No existing runs found. Generating new run ID.")
        
        # Initialize the agent with unique run ID and mode
        agent = SchemaAnalyzerAgent(OPENAI_API_KEY, run_id=run_id, mode=mode)
        
        # Run the analysis
        results = agent.run_analysis()
        
        if "error" not in results:
            print("\n" + "="*50)
            print("SCHEMA ANALYSIS COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"Run ID: {agent.run_id}")
            print(f"Mode: {agent.mode}")
            print(f"Results saved to: {agent.schema_dir}/schema_analysis_results.json")
            print(f"Tables analyzed: {len(results.get('tables', []))}")
            print(f"Cross-table relationships: {len(results.get('cross_table_relationships', []))}")
            print("\nKey findings:")
            
            for table in results.get('tables', []):
                print(f"- {table['table_name']}: Primary Key = {table['primary_key']}")
                if agent.mode == "full":
                    print(f"  Test scenarios: {len(table.get('test_scenarios', []))}")
                    print(f"  Business rules: {len(table.get('business_rules', []))}")
        else:
            print(f"Analysis failed: {results['error']}")
            
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 