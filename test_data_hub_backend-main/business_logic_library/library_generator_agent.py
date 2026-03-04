import os
import csv
import json
import logging
import pandas as pd
import openai
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY
from datetime import datetime
from schema_analyzer_agent import SchemaAnalyzerAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

class LibraryGeneratorAgent:
    def __init__(self, run_id: str = None, mode: str = "interactive"):
        """Initialize the Library Generator Agent.
        
        Args:
            run_id: Unique run ID (auto-generated if None)
            mode: Generation mode - "interactive" (chat-based) or "data_analysis" (from existing data)
        """
        self.run_id = run_id
        self.mode = mode
        
        # Define folder structure if run_id is provided
        if run_id:
            self.base_dir = "runs"
            self.run_dir = os.path.join(self.base_dir, self.run_id)
            self.input_data_dir = os.path.join(self.run_dir, "input_data")
            self.schema_dir = os.path.join(self.run_dir, "schema")
            self.synthetic_data_dir = os.path.join(self.run_dir, "synthetic_data")
            self.validation_dir = os.path.join(self.run_dir, "validation")
            
            # Create all necessary directories
            os.makedirs(self.run_dir, exist_ok=True)
            os.makedirs(self.input_data_dir, exist_ok=True)
            os.makedirs(self.schema_dir, exist_ok=True)
            os.makedirs(self.synthetic_data_dir, exist_ok=True)
            os.makedirs(self.validation_dir, exist_ok=True)
            os.makedirs(os.path.join(self.input_data_dir, "data"), exist_ok=True)
            os.makedirs(os.path.join(self.input_data_dir, "schema"), exist_ok=True)
            os.makedirs(os.path.join(self.synthetic_data_dir, "data"), exist_ok=True)
            os.makedirs(os.path.join(self.synthetic_data_dir, "scripts"), exist_ok=True)
            os.makedirs(os.path.join(self.validation_dir, "reports"), exist_ok=True)
            os.makedirs(os.path.join(self.validation_dir, "scripts"), exist_ok=True)
        
        self.business_logic_dir = "business_logic_library"
        self.test_scenarios_file = os.path.join(self.business_logic_dir, "test_scenarios.csv")
        self.business_rules_file = os.path.join(self.business_logic_dir, "business_rules.csv")
        
        self.ensure_files_exist()
        
    def ensure_files_exist(self):
        """Ensure the CSV files exist with headers."""
        # Ensure directory exists
        os.makedirs(self.business_logic_dir, exist_ok=True)
        
        # Business rules file
        if not os.path.exists(self.business_rules_file):
            with open(self.business_rules_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['table_name', 'rule_name', 'rule_type', 'description', 'validation_logic', 'error_message', 'severity', 'is_active'])
        
        # Test scenarios file
        if not os.path.exists(self.test_scenarios_file):
            with open(self.test_scenarios_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['table_name', 'scenario_name', 'scenario_type', 'description', 'test_conditions', 'expected_behavior', 'data_requirements', 'priority', 'is_active'])
    
    def load_existing_library(self):
        """Load existing business rules and test scenarios."""
        business_rules = []
        test_scenarios = []
        
        # Load business rules
        if os.path.exists(self.business_rules_file):
            with open(self.business_rules_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                business_rules = list(reader)
        
        # Load test scenarios
        if os.path.exists(self.test_scenarios_file):
            with open(self.test_scenarios_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                test_scenarios = list(reader)
        
        return business_rules, test_scenarios
    
    def load_schema_analysis(self):
        """Load schema analysis results from the run directory."""
        if not self.run_id:
            logger.error("No run_id provided, cannot load schema analysis")
            return None
        
        schema_file = os.path.join(self.schema_dir, "schema_analysis_results.json")
        if not os.path.exists(schema_file):
            logger.error(f"Schema analysis file not found: {schema_file}")
            return None
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading schema analysis: {str(e)}")
            return None
    
    def load_input_data(self):
        """Load input data files if they exist."""
        if not self.run_id:
            return {}
        
        data_files = {}
        
        # First try to load from the data subdirectory (where files are actually stored)
        data_subdir = os.path.join(self.input_data_dir, "data")
        if os.path.exists(data_subdir):
            for filename in os.listdir(data_subdir):
                if filename.endswith('.csv'):
                    file_path = os.path.join(data_subdir, filename)
                    try:
                        df = pd.read_csv(file_path)
                        table_name = filename.replace('.csv', '')
                        data_files[table_name] = df
                        logger.info(f"Loaded input data for {table_name}: {len(df)} records from {data_subdir}")
                    except Exception as e:
                        logger.error(f"Error loading {filename}: {str(e)}")
        
        # If no files found in data subdirectory, try the main input_data directory
        if not data_files and os.path.exists(self.input_data_dir):
            for filename in os.listdir(self.input_data_dir):
                if filename.endswith('.csv'):
                    file_path = os.path.join(self.input_data_dir, filename)
                    try:
                        df = pd.read_csv(file_path)
                        table_name = filename.replace('.csv', '')
                        data_files[table_name] = df
                        logger.info(f"Loaded input data for {table_name}: {len(df)} records from {self.input_data_dir}")
                    except Exception as e:
                        logger.error(f"Error loading {filename}: {str(e)}")
        
        return data_files
    
    def run_schema_analysis_if_needed(self):
        """Run schema analysis in schema_only mode if it doesn't exist."""
        if not self.run_id:
            logger.error("No run_id provided, cannot run schema analysis")
            return None
        
        schema_file = os.path.join(self.schema_dir, "schema_analysis_results.json")
        
        # Check if schema analysis already exists
        if os.path.exists(schema_file):
            logger.info("Schema analysis already exists, loading from file")
            return self.load_schema_analysis()
        
        # Run schema analysis in schema_only mode
        logger.info("Running schema analysis in schema_only mode...")
        try:
            schema_agent = SchemaAnalyzerAgent(OPENAI_API_KEY, self.run_id, mode="schema_only")
            results = schema_agent.run_analysis()
            
            if "error" not in results:
                logger.info("Schema analysis completed successfully")
                return results
            else:
                logger.error(f"Schema analysis failed: {results['error']}")
                return None
                
        except Exception as e:
            logger.error(f"Error running schema analysis: {str(e)}")
            return None
    
    def generate_from_data_analysis(self):
        """Generate business rules and test scenarios from existing data analysis."""
        print("\n📋 STEP 1: Data Loading & Analysis")
        logger.info("🔍 Loading input data for business logic generation...")
        
        # Load input data first
        input_data = self.load_input_data()
        
        if not input_data:
            logger.error("❌ Failed to load input data")
            return False
        
        logger.info(f"✅ Loaded {len(input_data)} input data tables")
        print(f"   📊 Input data tables: {', '.join(input_data.keys())}")
        
        # For functional test scenarios, we can generate business logic directly from data
        # without needing schema analysis first
        if self.mode == "data_analysis":
            print("\n📋 STEP 2: Direct Business Logic Generation from Data")
            logger.info("🚀 Generating business logic directly from uploaded data...")
            
            # Generate business rules and test scenarios directly from data
            business_rules, test_scenarios = self.generate_logic_from_data_only(input_data)
            
            if business_rules or test_scenarios:
                logger.info(f"✅ Generated {len(business_rules)} business rules and {len(test_scenarios)} test scenarios")
                print(f"   📊 Generated: {len(business_rules)} business rules, {len(test_scenarios)} test scenarios")
                
                # Deduplicate business logic before creating schema analysis
                unique_business_rules, unique_test_scenarios = self.deduplicate_business_logic(business_rules, test_scenarios)
                
                # Ensure we have the minimum required count
                final_business_rules, final_test_scenarios = self.ensure_minimum_count(unique_business_rules, unique_test_scenarios, target_min=3)
                
                # Integrate with existing schema analysis instead of overwriting it
                self.integrate_with_existing_schema_analysis(input_data, final_business_rules, final_test_scenarios)
                
                print("\n💾 STEP 3: Library Integration")
                logger.info("💾 Appending generated business logic to library...")
                
                # Append to library (but don't fail if this doesn't work)
                try:
                    success = self.append_to_library(final_business_rules, final_test_scenarios)
                    if success:
                        logger.info(f"✅ Successfully generated and added {len(final_business_rules)} business rules and {len(final_test_scenarios)} test scenarios")
                        print("   ✅ Business logic added to library")
                    else:
                        logger.warning("⚠️ Library append failed, but schema file was created successfully")
                        print("   ⚠️ Library append failed, but schema file was created successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Library append failed with error: {str(e)}, but schema file was created successfully")
                    print(f"   ⚠️ Library append failed with error: {str(e)}, but schema file was created successfully")
                
                # Return True if we successfully generated content and created schema file
                return True
            else:
                logger.warning("⚠️ No business rules or test scenarios generated from AI")
                logger.info("🔄 Creating fallback business rules and test scenarios...")
                
                # Create fallback business rules and test scenarios based on the data
                fallback_business_rules, fallback_test_scenarios = self.create_fallback_business_logic(input_data)
                
                if fallback_business_rules or fallback_test_scenarios:
                    logger.info(f"✅ Created fallback: {len(fallback_business_rules)} business rules, {len(fallback_test_scenarios)} test scenarios")
                    
                    # Deduplicate fallback business logic before creating schema analysis
                    unique_fallback_rules, unique_fallback_scenarios = self.deduplicate_business_logic(fallback_business_rules, fallback_test_scenarios)
                    
                    # Ensure we have the minimum required count
                    final_fallback_rules, final_fallback_scenarios = self.ensure_minimum_count(unique_fallback_rules, unique_fallback_scenarios, target_min=3)
                    
                    # Integrate with existing schema analysis instead of overwriting it
                    self.integrate_with_existing_schema_analysis(input_data, final_fallback_rules, final_fallback_scenarios)
                    return True
                else:
                    # Still create a basic schema analysis file for the UI
                    self.create_basic_schema_analysis(input_data, [], [])
                    return False
        
        # For other modes, continue with the original schema analysis approach
        print("\n📋 STEP 2: Schema Analysis Verification")
        logger.info("🔍 Verifying schema analysis exists for the run...")
        
        # Run or load schema analysis
        schema_analysis = self.run_schema_analysis_if_needed()
        if not schema_analysis:
            logger.error("❌ Failed to get schema analysis")
            return False
        
        logger.info("✅ Schema analysis verified")
        
        print("\n🤖 STEP 3: AI Business Logic Generation")
        logger.info("🚀 Engaging OpenAI GPT-4 for intelligent business logic generation...")
        print("   🔄 AI is analyzing data patterns and generating business rules...")
        
        # Generate business rules and test scenarios
        business_rules, test_scenarios = self.generate_logic_from_schema_and_data(schema_analysis, input_data)
        
        if business_rules or test_scenarios:
            logger.info(f"✅ Generated {len(business_rules)} business rules and {len(test_scenarios)} test scenarios")
            print(f"   📊 Generated: {len(business_rules)} business rules, {len(test_scenarios)} test scenarios")
            
            # Deduplicate business logic before appending to library
            unique_business_rules, unique_test_scenarios = self.deduplicate_business_logic(business_rules, test_scenarios)
            
            # Ensure we have the minimum required count
            final_business_rules, final_test_scenarios = self.ensure_minimum_count(unique_business_rules, unique_test_scenarios, target_min=3)
            
            print("\n💾 STEP 4: Library Integration")
            logger.info("💾 Appending generated business logic to library...")
            
            # Append to library
            success = self.append_to_library(final_business_rules, final_test_scenarios)
            if success:
                logger.info(f"✅ Successfully generated and added {len(final_business_rules)} business rules and {len(final_test_scenarios)} test scenarios")
                print("   ✅ Business logic added to library")
                return True
            else:
                logger.error("❌ Failed to append to library")
        
        return False
    
    def generate_logic_from_schema_and_data(self, schema_analysis, input_data):
        """Generate business rules and test scenarios from schema analysis and input data."""
        try:
            # Create analysis context
            analysis_context = {
                "schema_analysis": schema_analysis,
                "input_data_summary": {}
            }
            
            # Add input data summary
            for table_name, df in input_data.items():
                analysis_context["input_data_summary"][table_name] = {
                    "record_count": len(df),
                    "columns": list(df.columns),
                    "data_types": {col: str(dtype) for col, dtype in df.dtypes.to_dict().items()},
                    "unique_values": {col: df[col].nunique() for col in df.columns if df[col].dtype == 'object'},
                    "value_ranges": {col: {'min': df[col].min(), 'max': df[col].max()} 
                                   for col in df.columns if df[col].dtype in ['int64', 'float64']}
                }
            
            # Generate prompt for LLM
            prompt = self.create_data_analysis_prompt(analysis_context)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an EXPERT business analyst and test engineer specializing in FINANCIAL SYSTEMS and CREDIT CARD OPERATIONS. Your task is to generate EXACTLY 3-5 UNIQUE business rules and 3-5 UNIQUE test scenarios covering complex business logic.

CRITICAL REQUIREMENTS:
1. Generate EXACTLY 3-5 UNIQUE business rules and 3-5 UNIQUE test scenarios TOTAL
2. DISTRIBUTE EVENLY across different tables - don't concentrate on one table
3. EACH rule and scenario must be UNIQUE - no duplicate names, descriptions, or logic
4. Focus on COMPLEX BUSINESS LOGIC, not just data validation
5. Follow the exact CSV format specified in the user prompt
6. Use appropriate rule types: uniqueness, referential, range, enumeration, business_logic
7. Use appropriate scenario types: positive, negative, edge_case
8. Use appropriate priorities: HIGH, MEDIUM, LOW, CRITICAL
9. Use appropriate severities: CRITICAL, HIGH, MEDIUM, LOW
10. Make validation logic and test conditions specific and actionable
11. Ensure data requirements are clear and testable
12. Consider cross-table relationships when relevant
13. VALIDATION LOGIC MUST BE CHECK LOGIC ONLY: Use EXISTS, IN, NOT EXISTS, =, !=, >, <, etc. - NEVER use INSERT, UPDATE, DELETE statements

DISTRIBUTION GUIDELINES:
- If you have 3+ tables, generate 1-2 rules/scenarios per table
- If you have 2 tables, generate 2-3 rules/scenarios per table  
- If you have 1 table, generate 3-5 rules/scenarios for that table
- Ensure NO DUPLICATES across all tables

BUSINESS LOGIC FOCUS:
- Generate business rules that test CROSS-TABLE RELATIONSHIPS
- Focus on BUSINESS WORKFLOWS (KYC, card activation, fraud detection)
- Include REGULATORY COMPLIANCE rules (age restrictions, income validation)
- Cover RISK MANAGEMENT scenarios (credit risk, fraud risk)
- Test DATA INTEGRITY and referential integrity
- Include COMPLEX BUSINESS SCENARIOS that go beyond simple field validation

OUTPUT FORMAT:
Return a JSON object with "business_rules" and "test_scenarios" arrays.
Each item should match the CSV column structure exactly.
Generate EXACTLY 3-5 UNIQUE business rules and 3-5 UNIQUE test scenarios TOTAL.
Ensure NO DUPLICATES in rule names, descriptions, or validation logic.
Distribute evenly across different tables."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                json_str = content[start:end].strip()
            else:
                json_str = content
            
            # Parse JSON
            result = json.loads(json_str)
            
            return result.get('business_rules', []), result.get('test_scenarios', [])
            
        except Exception as e:
            logger.error(f"Error generating logic from schema and data: {str(e)}")
            return [], []
    
    def generate_logic_from_data_only(self, input_data):
        """Generate business rules and test scenarios directly from input data without schema analysis."""
        try:
            # Create analysis context from data only
            analysis_context = {
                "input_data_summary": {}
            }
            
            # Add input data summary with proper type conversion for JSON serialization
            for table_name, df in input_data.items():
                analysis_context["input_data_summary"][table_name] = {
                    "record_count": int(len(df)),
                    "columns": list(df.columns),
                    "data_types": {col: str(dtype) for col, dtype in df.dtypes.to_dict().items()},
                    "unique_values": {col: int(df[col].nunique()) for col in df.columns if df[col].dtype == 'object'},
                    "value_ranges": {col: {'min': float(df[col].min()) if pd.notna(df[col].min()) else None, 
                                         'max': float(df[col].max()) if pd.notna(df[col].max()) else None} 
                                   for col in df.columns if df[col].dtype in ['int64', 'float64']}
                }
            
            # Generate prompt for LLM
            prompt = self.create_data_analysis_prompt(analysis_context)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an EXPERT business analyst and test engineer specializing in FINANCIAL SYSTEMS and CREDIT CARD OPERATIONS. Your task is to generate EXACTLY 3-5 UNIQUE business rules and 3-5 UNIQUE test scenarios covering complex business logic.

CRITICAL REQUIREMENTS:
1. Generate EXACTLY 3-5 UNIQUE business rules and 3-5 UNIQUE test scenarios TOTAL
2. DISTRIBUTE EVENLY across different tables - don't concentrate on one table
3. EACH rule and scenario must be UNIQUE - no duplicate names, descriptions, or logic
4. Focus on COMPLEX BUSINESS LOGIC, not just data validation
5. Follow the exact CSV format specified in the user prompt
6. Use appropriate rule types: uniqueness, referential, range, enumeration, business_logic
7. Use appropriate scenario types: positive, negative, edge_case
8. Use appropriate priorities: HIGH, MEDIUM, LOW, CRITICAL
9. Use appropriate severities: CRITICAL, HIGH, MEDIUM, LOW
10. Make validation logic and test conditions specific and actionable
11. Ensure data requirements are clear and testable
12. Consider cross-table relationships when relevant
13. VALIDATION LOGIC MUST BE CHECK LOGIC ONLY: Use EXISTS, IN, NOT EXISTS, =, !=, >, <, etc. - NEVER use INSERT, UPDATE, DELETE statements

DISTRIBUTION GUIDELINES:
- If you have 3+ tables, generate 1-2 rules/scenarios per table
- If you have 2 tables, generate 2-3 rules/scenarios per table  
- If you have 1 table, generate 3-5 rules/scenarios for that table
- Ensure NO DUPLICATES across all tables

BUSINESS LOGIC FOCUS:
- Generate business rules that test CROSS-TABLE RELATIONSHIPS
- Focus on BUSINESS WORKFLOWS (KYC, card activation, fraud detection)
- Include REGULATORY COMPLIANCE rules (age restrictions, income validation)
- Cover RISK MANAGEMENT scenarios (credit risk, fraud risk)
- Test DATA INTEGRITY and referential integrity
- Include COMPLEX BUSINESS SCENARIOS that go beyond simple field validation

OUTPUT FORMAT:
Return a JSON object with "business_rules" and "test_scenarios" arrays.
Each item should match the CSV column structure exactly.
Generate EXACTLY 3-5 UNIQUE business rules and 3-5 UNIQUE test scenarios TOTAL.
Ensure NO DUPLICATES in rule names, descriptions, or validation logic.
Distribute evenly across different tables."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse response
            content = response.choices[0].message.content
            logger.info(f"OpenAI API response received: {len(content)} characters")
            
            # Log the first and last 200 characters for debugging
            logger.info(f"Response start: {content[:200]}...")
            logger.info(f"Response end: ...{content[-200:]}")
            
            # Try to extract JSON from response with multiple fallback methods
            try:
                # Method 1: Look for JSON content in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_content = content[start_idx:end_idx]
                    logger.info(f"Extracted JSON content: {len(json_content)} characters")
                    logger.info(f"JSON start: {json_content[:200]}...")
                    logger.info(f"JSON end: ...{json_content[-200:]}")
                    
                    # Try to parse the extracted JSON
                    try:
                        result = json.loads(json_content)
                        business_rules = result.get('business_rules', [])
                        test_scenarios = result.get('test_scenarios', [])
                        
                        logger.info(f"Successfully parsed OpenAI response: {len(business_rules)} business rules, {len(test_scenarios)} test scenarios")
                        return business_rules, test_scenarios
                    except json.JSONDecodeError as json_error:
                        logger.warning(f"First JSON extraction failed: {str(json_error)}, trying fallback methods...")
                        
                        # Method 2: Try to find complete JSON objects
                        import re
                        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                        json_matches = re.findall(json_pattern, content)
                        
                        for match in json_matches:
                            try:
                                result = json.loads(match)
                                if 'business_rules' in result or 'test_scenarios' in result:
                                    business_rules = result.get('business_rules', [])
                                    test_scenarios = result.get('test_scenarios', [])
                                    
                                    logger.info(f"Fallback JSON parsing successful: {len(business_rules)} business rules, {len(test_scenarios)} test scenarios")
                                    return business_rules, test_scenarios
                            except json.JSONDecodeError:
                                continue
                        
                        # Method 3: Try to extract just the arrays if the outer object is malformed
                        business_rules_match = re.search(r'"business_rules"\s*:\s*(\[.*?\])', content, re.DOTALL)
                        test_scenarios_match = re.search(r'"test_scenarios"\s*:\s*(\[.*?\])', content, re.DOTALL)
                        
                        business_rules = []
                        test_scenarios = []
                        
                        if business_rules_match:
                            try:
                                business_rules = json.loads(business_rules_match.group(1))
                                logger.info(f"Extracted business_rules array: {len(business_rules)} rules")
                            except json.JSONDecodeError:
                                logger.warning("Failed to parse business_rules array")
                        
                        if test_scenarios_match:
                            try:
                                test_scenarios = json.loads(test_scenarios_match.group(1))
                                logger.info(f"Extracted test_scenarios array: {len(test_scenarios)} scenarios")
                            except json.JSONDecodeError:
                                logger.warning("Failed to parse test_scenarios array")
                        
                        if business_rules or test_scenarios:
                            logger.info(f"Partial extraction successful: {len(business_rules)} business rules, {len(test_scenarios)} test scenarios")
                            return business_rules, test_scenarios
                        
                        logger.error("All JSON extraction methods failed")
                        return [], []
                        
                else:
                    logger.error("No JSON content found in OpenAI response")
                    logger.error(f"Content search: start_idx={start_idx}, end_idx={end_idx}")
                    return [], []
                    
            except Exception as e:
                logger.error(f"Unexpected error during JSON extraction: {str(e)}")
                logger.error(f"Response content: {content}")
                return [], []
                
        except Exception as e:
            logger.error(f"Error generating logic from data: {str(e)}")
            return [], []
    
    def create_basic_schema_analysis(self, input_data, business_rules, test_scenarios):
        """Create a basic schema analysis results file for the UI when generating directly from data."""
        try:
            if not self.run_id:
                return
            
            # Apply our improved deduplication and minimum count system
            logger.info("Applying deduplication and minimum count to schema analysis...")
            unique_business_rules, unique_test_scenarios = self.deduplicate_business_logic(business_rules, test_scenarios)
            final_business_rules, final_test_scenarios = self.ensure_minimum_count(unique_business_rules, unique_test_scenarios, target_min=3)
            
            logger.info(f"Schema analysis: {len(final_business_rules)} business rules, {len(final_test_scenarios)} test scenarios")
            
            # Ensure the schema directory exists
            os.makedirs(self.schema_dir, exist_ok=True)
            
            schema_file = os.path.join(self.schema_dir, "schema_analysis_results.json")
            
            # Create basic schema analysis structure
            schema_analysis = {
                "run_id": self.run_id,
                "generated_at": datetime.now().isoformat(),
                "mode": "data_analysis",
                "tables": [],
                "cross_table_relationships": self.validate_cross_table_relationships([
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
                ])
            }
            
            # Add table information from input data
            for table_name, df in input_data.items():
                table_info = {
                    "table_name": table_name,
                    "record_count": int(len(df)),
                    "columns": [],
                    "business_rules": [],
                    "test_scenarios": [],
                    "data_generation_rules": []
                }
                
                # Add column information
                for col in df.columns:
                    col_info = {
                        "column_name": col,
                        "data_type": str(df[col].dtype),
                        "is_nullable": bool(df[col].isna().any()),
                        "unique_values": int(df[col].nunique()) if df[col].dtype == 'object' else None,
                        "min_value": float(df[col].min()) if df[col].dtype in ['int64', 'float64'] and pd.notna(df[col].min()) else None,
                        "max_value": float(df[col].max()) if df[col].dtype in ['int64', 'float64'] and pd.notna(df[col].max()) else None
                    }
                    table_info["columns"].append(col_info)
                
                # Add business rules for this table (already deduplicated and with minimum count)
                for rule in final_business_rules:
                    if rule.get('table_name') == table_name:
                        table_info["business_rules"].append({
                            "rule_name": rule.get('rule_name'),
                            "description": rule.get('description'),
                            "validation_logic": rule.get('validation_logic'),
                            "error_message": rule.get('error_message'),
                            "rule_type": rule.get('rule_type', 'business_logic'),
                            "severity": rule.get('severity', 'MEDIUM')
                        })
                
                # Add test scenarios for this table (already deduplicated and with minimum count)
                for scenario in final_test_scenarios:
                    if scenario.get('table_name') == table_name:
                        table_info["test_scenarios"].append({
                            "scenario_name": scenario.get('scenario_name'),
                            "description": scenario.get('description'),
                            "test_type": scenario.get('scenario_type'),
                            "business_logic": scenario.get('test_conditions'),
                            "expected_behavior": scenario.get('expected_behavior'),
                            "data_requirements": scenario.get('data_requirements'),
                            "priority": scenario.get('priority', 'MEDIUM')
                        })
                
                # Add the table info to the schema analysis
                schema_analysis["tables"].append(table_info)
            
            # Save the schema analysis results
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema_analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created basic schema analysis results file: {schema_file}")
            
            # Verify the file was created and is readable
            if os.path.exists(schema_file):
                file_size = os.path.getsize(schema_file)
                logger.info(f"✅ Schema analysis file created successfully: {schema_file} (size: {file_size} bytes)")
                
                # Try to read the file back to verify it's valid
                try:
                    with open(schema_file, 'r', encoding='utf-8') as f:
                        test_read = json.load(f)
                    logger.info(f"✅ Schema analysis file is valid JSON with {len(test_read.get('tables', []))} tables")
                except Exception as read_error:
                    logger.error(f"❌ Schema analysis file created but cannot be read: {read_error}")
            else:
                logger.error(f"❌ Schema analysis file was not created: {schema_file}")
            
            # Update the run configuration to reflect that schema analysis is complete
            self.update_run_config_schema_status()
            
        except Exception as e:
            logger.error(f"Error creating basic schema analysis: {str(e)}")
    
    def deduplicate_business_logic(self, business_rules, test_scenarios):
        """Remove duplicate business rules and test scenarios based on content similarity."""
        try:
            # Deduplicate business rules - be less aggressive to maintain count
            seen_rules = set()
            unique_rules = []
            
            for rule in business_rules:
                # Create a unique key for deduplication - only check exact duplicates
                rule_key = f"{rule.get('table_name', '')}_{rule.get('rule_name', '')}"
                if rule_key not in seen_rules:
                    seen_rules.add(rule_key)
                    unique_rules.append(rule)
                else:
                    # Check if this is truly a duplicate by comparing more fields
                    existing_rule = next((r for r in unique_rules if f"{r.get('table_name', '')}_{r.get('rule_name', '')}" == rule_key), None)
                    if existing_rule:
                        # Only remove if description and validation logic are identical
                        if (existing_rule.get('description') == rule.get('description') and 
                            existing_rule.get('validation_logic') == rule.get('validation_logic')):
                            logger.info(f"Removing exact duplicate rule: {rule.get('rule_name')}")
                            continue
                        else:
                            # Similar name but different content - keep it with a modified name
                            rule['rule_name'] = f"{rule.get('rule_name')}_Variant"
                            unique_rules.append(rule)
                            logger.info(f"Keeping rule variant: {rule['rule_name']}")
                    else:
                        unique_rules.append(rule)
            
            # Deduplicate test scenarios - be less aggressive to maintain count
            seen_scenarios = set()
            unique_scenarios = []
            
            for scenario in test_scenarios:
                # Create a unique key for deduplication - only check exact duplicates
                scenario_key = f"{scenario.get('table_name', '')}_{scenario.get('scenario_name', '')}"
                if scenario_key not in seen_scenarios:
                    seen_scenarios.add(scenario_key)
                    unique_scenarios.append(scenario)
                else:
                    # Check if this is truly a duplicate by comparing more fields
                    existing_scenario = next((s for s in unique_scenarios if f"{s.get('table_name', '')}_{s.get('scenario_name', '')}" == scenario_key), None)
                    if existing_scenario:
                        # Only remove if description and test conditions are identical
                        if (existing_scenario.get('description') == scenario.get('description') and 
                            existing_scenario.get('test_conditions') == scenario.get('test_conditions')):
                            logger.info(f"Removing exact duplicate scenario: {scenario.get('scenario_name')}")
                            continue
                        else:
                            # Similar name but different content - keep it with a modified name
                            scenario['scenario_name'] = f"{scenario.get('scenario_name')}_Variant"
                            unique_scenarios.append(scenario)
                            logger.info(f"Keeping scenario variant: {scenario['scenario_name']}")
                    else:
                        unique_scenarios.append(scenario)
            
            # Log deduplication results
            original_rules = len(business_rules)
            original_scenarios = len(test_scenarios)
            final_rules = len(unique_rules)
            final_scenarios = len(unique_scenarios)
            
            if original_rules > final_rules:
                logger.info(f"Removed {original_rules - final_rules} exact duplicate business rules")
            if original_scenarios > final_scenarios:
                logger.info(f"Removed {original_scenarios - final_scenarios} exact duplicate test scenarios")
            
            # Ensure we have the minimum required count
            if final_rules < 3:
                logger.warning(f"Warning: Only {final_rules} business rules after deduplication (minimum 3 recommended)")
            if final_scenarios < 3:
                logger.warning(f"Warning: Only {final_scenarios} test scenarios after deduplication (minimum 3 recommended)")
            
            logger.info(f"Deduplication complete: {final_rules} unique rules, {final_scenarios} unique scenarios")
            return unique_rules, unique_scenarios
            
        except Exception as e:
            logger.error(f"Error during deduplication: {str(e)}")
            return business_rules, test_scenarios
    
    def ensure_minimum_count(self, business_rules, test_scenarios, target_min=3):
        """Ensure we have at least the minimum required count by generating additional items if needed."""
        try:
            current_rules = len(business_rules)
            current_scenarios = len(test_scenarios)
            
            # If we have enough, return as is
            if current_rules >= target_min and current_scenarios >= target_min:
                return business_rules, test_scenarios
            
            logger.info(f"Ensuring minimum count: rules={current_rules}/{target_min}, scenarios={current_scenarios}/{target_min}")
            
            # Generate additional business rules if needed
            if current_rules < target_min:
                additional_rules_needed = target_min - current_rules
                logger.info(f"Generating {additional_rules_needed} additional business rules")
                
                # Get unique table names from existing rules
                existing_tables = set(rule.get('table_name', '') for rule in business_rules)
                all_tables = ['customer_info', 'credit_card_accounts', 'credit_card_products', 'credit_card_transactions', 'imobile_user_session']
                
                # Find tables that don't have rules yet
                available_tables = [table for table in all_tables if table not in existing_tables]
                if not available_tables:
                    available_tables = all_tables  # Use all tables if all have rules
                
                for i in range(additional_rules_needed):
                    table_name = available_tables[i % len(available_tables)]
                    new_rule = self.generate_additional_business_rule(table_name, i + 1)
                    if new_rule:
                        business_rules.append(new_rule)
                        logger.info(f"Generated additional business rule: {new_rule['rule_name']}")
            
            # Generate additional test scenarios if needed
            if current_scenarios < target_min:
                additional_scenarios_needed = target_min - current_scenarios
                logger.info(f"Generating {additional_scenarios_needed} additional test scenarios")
                
                # Get unique table names from existing scenarios
                existing_tables = set(scenario.get('table_name', '') for scenario in test_scenarios)
                all_tables = ['customer_info', 'credit_card_accounts', 'credit_card_products', 'credit_card_transactions', 'imobile_user_session']
                
                # Find tables that don't have scenarios yet
                available_tables = [table for table in all_tables if table not in existing_tables]
                if not available_tables:
                    available_tables = all_tables  # Use all tables if all have scenarios
                
                for i in range(additional_scenarios_needed):
                    table_name = available_tables[i % len(available_tables)]
                    new_scenario = self.generate_additional_test_scenario(table_name, i + 1)
                    if new_scenario:
                        test_scenarios.append(new_scenario)
                        logger.info(f"Generated additional test scenario: {new_scenario['scenario_name']}")
            
            final_rules = len(business_rules)
            final_scenarios = len(test_scenarios)
            logger.info(f"Final count after ensuring minimum: rules={final_rules}, scenarios={final_scenarios}")
            
            return business_rules, test_scenarios
            
        except Exception as e:
            logger.error(f"Error ensuring minimum count: {str(e)}")
            return business_rules, test_scenarios
    
    def generate_additional_business_rule(self, table_name, index):
        """Generate an additional business rule for a specific table."""
        try:
            rule_templates = {
                'customer_info': [
                    {
                        'rule_name': 'Customer Data Validation',
                        'rule_type': 'business_logic',
                        'description': 'Customer data must be complete and valid',
                        'validation_logic': 'customer_id IS NOT NULL AND birth_date IS NOT NULL',
                        'error_message': 'Customer data incomplete',
                        'severity': 'MEDIUM'
                    },
                    {
                        'rule_name': 'Customer Age Verification',
                        'rule_type': 'range',
                        'description': 'Customer age must be within valid range',
                        'validation_logic': 'age >= 18 AND age <= 100',
                        'error_message': 'Customer age out of valid range',
                        'severity': 'HIGH'
                    }
                ],
                'credit_card_accounts': [
                    {
                        'rule_name': 'Account Status Validation',
                        'rule_type': 'enumeration',
                        'description': 'Account status must be valid',
                        'validation_logic': "status IN ('Active', 'Inactive', 'Closed', 'Suspended')",
                        'error_message': 'Invalid account status',
                        'severity': 'HIGH'
                    },
                    {
                        'rule_name': 'Credit Limit Validation',
                        'rule_type': 'range',
                        'description': 'Credit limit must be positive',
                        'validation_logic': 'credit_limit > 0',
                        'error_message': 'Credit limit must be positive',
                        'severity': 'CRITICAL'
                    }
                ],
                'credit_card_products': [
                    {
                        'rule_name': 'Product Configuration',
                        'rule_type': 'business_logic',
                        'description': 'Product must have valid configuration',
                        'validation_logic': 'product_code IS NOT NULL AND interest_rate >= 0',
                        'error_message': 'Invalid product configuration',
                        'severity': 'HIGH'
                    },
                    {
                        'rule_name': 'Product Dates Validation',
                        'rule_type': 'business_logic',
                        'description': 'Product dates must be valid',
                        'validation_logic': 'start_date < end_date',
                        'error_message': 'Invalid product dates',
                        'severity': 'MEDIUM'
                    }
                ],
                'credit_card_transactions': [
                    {
                        'rule_name': 'Transaction Amount Validation',
                        'rule_type': 'range',
                        'description': 'Transaction amount must be positive',
                        'validation_logic': 'transaction_amount > 0',
                        'error_message': 'Transaction amount must be positive',
                        'severity': 'HIGH'
                    },
                    {
                        'rule_name': 'Transaction Date Validation',
                        'rule_type': 'business_logic',
                        'description': 'Transaction date must be valid',
                        'validation_logic': 'transaction_date <= CURRENT_DATE',
                        'error_message': 'Invalid transaction date',
                        'severity': 'MEDIUM'
                    }
                ],
                'imobile_user_session': [
                    {
                        'rule_name': 'Session Security',
                        'rule_type': 'business_logic',
                        'description': 'Session must have valid security parameters',
                        'validation_logic': 'session_id IS NOT NULL AND customer_id IS NOT NULL',
                        'error_message': 'Invalid session security parameters',
                        'severity': 'CRITICAL'
                    },
                    {
                        'rule_name': 'Session Duration Validation',
                        'rule_type': 'range',
                        'description': 'Session duration must be reasonable',
                        'validation_logic': 'session_duration > 0 AND session_duration <= 7200',
                        'error_message': 'Invalid session duration',
                        'severity': 'MEDIUM'
                    }
                ]
            }
            
            templates = rule_templates.get(table_name, [])
            if templates:
                template = templates[index % len(templates)]
                return {
                    'table_name': table_name,
                    'rule_name': f"{template['rule_name']}_{index}",
                    'rule_type': template['rule_type'],
                    'description': template['description'],
                    'validation_logic': template['validation_logic'],
                    'error_message': template['error_message'],
                    'severity': template['severity'],
                    'is_active': 1
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating additional business rule: {str(e)}")
            return None
    
    def generate_additional_test_scenario(self, table_name, index):
        """Generate an additional test scenario for a specific table."""
        try:
            scenario_templates = {
                'customer_info': [
                    {
                        'scenario_name': 'Customer Validation Test',
                        'scenario_type': 'positive',
                        'description': 'Test valid customer data',
                        'test_conditions': 'All required fields are present',
                        'expected_behavior': 'Customer record is accepted',
                        'data_requirements': 'Complete customer data',
                        'priority': 'HIGH'
                    },
                    {
                        'scenario_name': 'Customer Age Test',
                        'scenario_type': 'edge_case',
                        'description': 'Test customer age boundaries',
                        'test_conditions': 'Age is exactly 18 or 100',
                        'expected_behavior': 'Customer record is accepted',
                        'data_requirements': 'Customer with boundary age',
                        'priority': 'MEDIUM'
                    }
                ],
                'credit_card_accounts': [
                    {
                        'scenario_name': 'Account Status Test',
                        'scenario_type': 'positive',
                        'description': 'Test valid account status',
                        'test_conditions': 'Status is one of valid values',
                        'expected_behavior': 'Account is accepted',
                        'data_requirements': 'Account with valid status',
                        'priority': 'HIGH'
                    },
                    {
                        'scenario_name': 'Credit Limit Test',
                        'scenario_type': 'edge_case',
                        'description': 'Test credit limit boundaries',
                        'test_conditions': 'Credit limit is minimum valid amount',
                        'expected_behavior': 'Account is accepted',
                        'data_requirements': 'Account with minimum credit limit',
                        'priority': 'MEDIUM'
                    }
                ],
                'credit_card_products': [
                    {
                        'scenario_name': 'Product Configuration Test',
                        'scenario_type': 'positive',
                        'description': 'Test valid product configuration',
                        'test_conditions': 'Product has all required fields',
                        'expected_behavior': 'Product is accepted',
                        'data_requirements': 'Complete product configuration',
                        'priority': 'HIGH'
                    },
                    {
                        'scenario_name': 'Product Dates Test',
                        'scenario_type': 'edge_case',
                        'description': 'Test product date boundaries',
                        'test_conditions': 'Start and end dates are valid',
                        'expected_behavior': 'Product is accepted',
                        'data_requirements': 'Product with valid dates',
                        'priority': 'MEDIUM'
                    }
                ],
                'credit_card_transactions': [
                    {
                        'scenario_name': 'Transaction Amount Test',
                        'scenario_type': 'positive',
                        'description': 'Test valid transaction amount',
                        'test_conditions': 'Amount is positive and reasonable',
                        'expected_behavior': 'Transaction is accepted',
                        'data_requirements': 'Transaction with valid amount',
                        'priority': 'HIGH'
                    },
                    {
                        'scenario_name': 'Transaction Date Test',
                        'scenario_type': 'edge_case',
                        'description': 'Test transaction date boundaries',
                        'test_conditions': 'Date is current or past',
                        'expected_behavior': 'Transaction is accepted',
                        'data_requirements': 'Transaction with valid date',
                        'priority': 'MEDIUM'
                    }
                ],
                'imobile_user_session': [
                    {
                        'scenario_name': 'Session Security Test',
                        'scenario_type': 'positive',
                        'description': 'Test valid session security',
                        'test_conditions': 'All security parameters are present',
                        'expected_behavior': 'Session is accepted',
                        'data_requirements': 'Session with security parameters',
                        'priority': 'CRITICAL'
                    },
                    {
                        'scenario_name': 'Session Duration Test',
                        'scenario_type': 'edge_case',
                        'description': 'Test session duration boundaries',
                        'test_conditions': 'Duration is within valid range',
                        'expected_behavior': 'Session is accepted',
                        'data_requirements': 'Session with valid duration',
                        'priority': 'MEDIUM'
                    }
                ]
            }
            
            templates = scenario_templates.get(table_name, [])
            if templates:
                template = templates[index % len(templates)]
                return {
                    'table_name': table_name,
                    'scenario_name': f"{template['scenario_name']}_{index}",
                    'scenario_type': template['scenario_type'],
                    'description': template['description'],
                    'test_conditions': template['test_conditions'],
                    'expected_behavior': template['expected_behavior'],
                    'data_requirements': template['data_requirements'],
                    'priority': template['priority'],
                    'is_active': 1
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating additional test scenario: {str(e)}")
            return None
    
    def validate_cross_table_relationships(self, relationships):
        """Validate and fix cross-table relationships to ensure proper UI formatting."""
        try:
            valid_relationships = []
            
            # Define expected relationships based on the schema
            expected_relationships = [
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
            
            # Use expected relationships to ensure consistency
            for expected_rel in expected_relationships:
                # Check if this relationship exists in the input
                found = False
                for rel in relationships:
                    if (rel.get('from_table') == expected_rel['from_table'] and 
                        rel.get('to_table') == expected_rel['to_table']):
                        # Use the input relationship but ensure it has all required fields
                        valid_rel = {
                            "from_table": rel.get('from_table', expected_rel['from_table']),
                            "to_table": rel.get('to_table', expected_rel['to_table']),
                            "relationship_type": rel.get('relationship_type', expected_rel['relationship_type']),
                            "description": rel.get('description', expected_rel['description']),
                            "foreign_key": rel.get('foreign_key', expected_rel['foreign_key'])
                        }
                        valid_relationships.append(valid_rel)
                        found = True
                        break
                
                # If not found in input, add the expected one
                if not found:
                    valid_relationships.append(expected_rel)
            
            logger.info(f"Validated cross-table relationships: {len(valid_relationships)} relationships")
            return valid_relationships
            
        except Exception as e:
            logger.error(f"Error validating cross-table relationships: {str(e)}")
            # Return default relationships if validation fails
            return [
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
    
    def update_run_config_schema_status(self):
        """Update the run configuration to reflect that schema analysis is complete."""
        try:
            if not self.run_id:
                return
            
            config_file = os.path.join(self.run_dir, "run_config.json")
            if not os.path.exists(config_file):
                logger.warning(f"Run configuration file not found: {config_file}")
                return
            
            # Load existing configuration
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Update schema status
            if 'status' not in config:
                config['status'] = {}
            
            config['status']['has_schema'] = True
            config['status']['schema_generated_at'] = datetime.now().isoformat()
            config['schema_analysis_file'] = os.path.join("schema", "schema_analysis_results.json")
            
            # Save updated configuration
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated run configuration schema status for run {self.run_id}")
            
        except Exception as e:
            logger.error(f"Error updating run configuration schema status: {str(e)}")
    
    def analyze_table_data(self, table_data, table_name):
        """Analyze table data to understand business context and patterns."""
        try:
            logger.info(f"🔍 Analyzing data for table: {table_name}")
            
            analysis = {
                "table_name": table_name,
                "record_count": len(table_data),
                "columns": list(table_data.columns),
                "data_types": {},
                "value_distributions": {},
                "business_patterns": {},
                "data_quality_issues": [],
                "cross_table_relationships": []
            }
            
            # Analyze each column
            for col in table_data.columns:
                col_data = table_data[col]
                
                # Data type analysis
                analysis["data_types"][col] = str(col_data.dtype)
                
                # Value distribution analysis
                if col_data.dtype in ['int64', 'float64']:
                    # Numeric column analysis
                    min_val = float(col_data.min()) if pd.notna(col_data.min()) else None
                    max_val = float(col_data.max()) if pd.notna(col_data.max()) else None
                    mean_val = float(col_data.mean()) if pd.notna(col_data.mean()) else None
                    
                    analysis["value_distributions"][col] = {
                        "type": "numeric",
                        "min": min_val,
                        "max": max_val,
                        "mean": mean_val,
                        "null_count": int(col_data.isna().sum()),
                        "unique_count": int(col_data.nunique())
                    }
                    
                    # Business pattern detection for numeric columns
                    if 'age' in col.lower():
                        analysis["business_patterns"][col] = "Customer age field - likely has business rules for minors/seniors"
                    elif 'income' in col.lower() or 'salary' in col.lower():
                        analysis["business_patterns"][col] = "Income field - likely has validation rules and segmentation logic"
                    elif 'amount' in col.lower() or 'value' in col.lower():
                        analysis["business_patterns"][col] = "Monetary amount - likely has range validation and business rules"
                    elif 'limit' in col.lower():
                        analysis["business_patterns"][col] = "Credit limit field - likely has business rules based on customer profile"
                        
                elif col_data.dtype == 'object':
                    # String column analysis
                    unique_values = col_data.value_counts().head(10).to_dict()
                    null_count = int(col_data.isna().sum())
                    
                    analysis["value_distributions"][col] = {
                        "type": "categorical",
                        "unique_values": {str(k): int(v) for k, v in unique_values.items()},
                        "null_count": null_count,
                        "unique_count": int(col_data.nunique())
                    }
                    
                    # Business pattern detection for string columns
                    if 'status' in col.lower():
                        analysis["business_patterns"][col] = "Status field - likely has enumeration validation and business rules"
                    elif 'type' in col.lower():
                        analysis["business_patterns"][col] = "Type field - likely has category validation and business logic"
                    elif 'country' in col.lower() or 'nationality' in col.lower():
                        analysis["business_patterns"][col] = "Geographic field - likely has compliance and business rules"
                    elif 'kyc' in col.lower():
                        analysis["business_patterns"][col] = "KYC field - likely has regulatory compliance rules"
                        
                # Data quality analysis
                if col_data.isna().sum() > len(col_data) * 0.1:  # More than 10% nulls
                    analysis["data_quality_issues"].append(f"High null rate in {col}: {col_data.isna().sum()}/{len(col_data)}")
                
                if col_data.dtype == 'object' and col_data.nunique() == 1:
                    analysis["data_quality_issues"].append(f"Low variability in {col}: only {col_data.nunique()} unique values")
            
            # Cross-table relationship detection
            if 'customer_id' in table_data.columns:
                analysis["cross_table_relationships"].append("customer_id - likely references customer_info table")
            if 'serial_number' in table_data.columns:
                analysis["cross_table_relationships"].append("serial_number - likely references credit_card_accounts table")
            if 'session_id' in table_data.columns:
                analysis["cross_table_relationships"].append("session_id - likely unique identifier for sessions")
            
            logger.info(f"✅ Data analysis completed for {table_name}: {len(analysis['business_patterns'])} business patterns identified")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing table data for {table_name}: {str(e)}")
            return {}

    def create_fallback_business_logic(self, input_data):
        """Create fallback business rules and test scenarios when AI generation fails."""
        try:
            business_rules = []
            test_scenarios = []
            
            for table_name, df in input_data.items():
                # Create basic business rules based on data types
                if 'customer_info' in table_name.lower():
                    business_rules.append({
                        "table_name": table_name,
                        "rule_name": "Customer Age Validation",
                        "rule_type": "range",
                        "description": "Customer age must be between 18 and 100 years",
                        "validation_logic": "age >= 18 AND age <= 100",
                        "error_message": "Customer age must be between 18 and 100 years",
                        "severity": "HIGH",
                        "is_active": 1
                    })
                    
                    business_rules.append({
                        "table_name": table_name,
                        "rule_name": "Customer Status Validation",
                        "rule_type": "enumeration",
                        "description": "Customer status must be one of: active, inactive, closed",
                        "validation_logic": "status IN ('active', 'inactive', 'closed')",
                        "error_message": "Invalid customer status",
                        "severity": "MEDIUM",
                        "is_active": 1
                    })
                    
                    test_scenarios.append({
                        "table_name": table_name,
                        "scenario_name": "Valid Customer Age",
                        "scenario_type": "positive",
                        "description": "Test customer with valid age (18-100)",
                        "test_conditions": "age >= 18 AND age <= 100",
                        "expected_behavior": "Customer record is accepted",
                        "data_requirements": "Customer with age between 18 and 100",
                        "priority": "HIGH",
                        "is_active": 1
                    })
                    
                    test_scenarios.append({
                        "table_name": table_name,
                        "scenario_name": "Invalid Customer Age",
                        "scenario_type": "negative",
                        "description": "Test customer with invalid age (<18 or >100)",
                        "test_conditions": "age < 18 OR age > 100",
                        "expected_behavior": "Customer record is rejected",
                        "data_requirements": "Customer with age <18 or >100",
                        "priority": "HIGH",
                        "is_active": 1
                    })
                
                elif 'imobile_user_session' in table_name.lower():
                    business_rules.append({
                        "table_name": table_name,
                        "rule_name": "Session Duration Validation",
                        "rule_type": "range",
                        "description": "Session duration must be positive",
                        "validation_logic": "session_duration > 0",
                        "error_message": "Session duration must be positive",
                        "severity": "MEDIUM",
                        "is_active": 1
                    })
                    
                    test_scenarios.append({
                        "table_name": table_name,
                        "scenario_name": "Valid Session Duration",
                        "scenario_type": "positive",
                        "description": "Test session with positive duration",
                        "test_conditions": "session_duration > 0",
                        "expected_behavior": "Session is accepted",
                        "data_requirements": "Session with positive duration",
                        "priority": "MEDIUM",
                        "is_active": 1
                    })
                
                elif 'credit_card_accounts' in table_name.lower():
                    business_rules.append({
                        "table_name": table_name,
                        "rule_name": "Credit Limit Validation",
                        "rule_type": "range",
                        "description": "Credit limit must be positive",
                        "validation_logic": "credit_limit > 0",
                        "error_message": "Credit limit must be positive",
                        "severity": "HIGH",
                        "is_active": 1
                    })
                    
                    test_scenarios.append({
                        "table_name": table_name,
                        "scenario_name": "Valid Credit Limit",
                        "scenario_type": "positive",
                        "description": "Test account with valid credit limit",
                        "test_conditions": "credit_limit > 0",
                        "expected_behavior": "Account is accepted",
                        "data_requirements": "Account with positive credit limit",
                        "priority": "HIGH",
                        "is_active": 1
                    })
                
                elif 'credit_card_transactions' in table_name.lower():
                    business_rules.append({
                        "table_name": table_name,
                        "rule_name": "Transaction Amount Validation",
                        "rule_type": "range",
                        "description": "Transaction amount must be positive",
                        "validation_logic": "transaction_amount > 0",
                        "error_message": "Transaction amount must be positive",
                        "severity": "HIGH",
                        "is_active": 1
                    })
                    
                    test_scenarios.append({
                        "table_name": table_name,
                        "scenario_name": "Valid Transaction Amount",
                        "scenario_type": "positive",
                        "description": "Test transaction with valid amount",
                        "test_conditions": "transaction_amount > 0",
                        "expected_behavior": "Transaction is accepted",
                        "data_requirements": "Transaction with positive amount",
                        "priority": "HIGH",
                        "is_active": 1
                    })
                
                elif 'credit_card_products' in table_name.lower():
                    business_rules.append({
                        "table_name": table_name,
                        "rule_name": "Product Active Status",
                        "rule_type": "business_logic",
                        "description": "Product must be active for issuing new cards",
                        "validation_logic": "active_flag = 'Y'",
                        "error_message": "Inactive product used for issuing new cards",
                        "severity": "HIGH",
                        "is_active": 1
                    })
                    
                    test_scenarios.append({
                        "table_name": table_name,
                        "scenario_name": "Test Inactive Product Issuance",
                        "scenario_type": "negative",
                        "description": "Test scenario where an inactive product is used for issuing a card",
                        "test_conditions": "active_flag = 'N'",
                        "expected_behavior": "Product issuance should be rejected",
                        "data_requirements": "Product with active_flag = 'N'",
                        "priority": "HIGH",
                        "is_active": 1
                    })
            
            logger.info(f"Created fallback: {len(business_rules)} business rules, {len(test_scenarios)} test scenarios")
            return business_rules, test_scenarios
            
        except Exception as e:
            logger.error(f"Error creating fallback business logic: {str(e)}")
            return [], []

    def create_data_analysis_prompt(self, analysis_context):
        """Create prompt for data analysis-based business logic generation."""
        
        # Check if we have schema analysis or just input data
        has_schema_analysis = 'schema_analysis' in analysis_context and analysis_context['schema_analysis']
        
        schema_section = ""
        if has_schema_analysis:
            schema_section = f"""
SCHEMA ANALYSIS:
{json.dumps(analysis_context['schema_analysis'], indent=2)}
"""
        else:
            schema_section = """
SCHEMA ANALYSIS: None available - generating directly from data patterns
"""
        
        return f"""
You are an EXPERT business analyst specializing in FINANCIAL SYSTEMS. Generate EXACTLY 3-5 UNIQUE business rules and 3-5 UNIQUE test scenarios.

{schema_section}
INPUT DATA SUMMARY:
{json.dumps(analysis_context['input_data_summary'], indent=2)}

AVAILABLE TABLES: {', '.join(analysis_context['input_data_summary'].keys())}

## 📋 CRITICAL REQUIREMENTS:

1. **EXACTLY 3-5 business rules and 3-5 test scenarios TOTAL**
2. **DISTRIBUTE EVENLY across different tables** - don't concentrate on one table
3. **EACH rule and scenario must be UNIQUE** - no duplicate names, descriptions, or logic
4. **Cover different business aspects**: validation, business logic, referential integrity, compliance
5. **Use different rule types**: uniqueness, referential, range, enumeration, business_logic
6. **Use different scenario types**: positive, negative, edge_case

## 📊 DISTRIBUTION GUIDELINES:

- If you have 3 tables, generate 1-2 rules/scenarios per table
- If you have 2 tables, generate 2-3 rules/scenarios per table  
- If you have 1 table, generate 3-5 rules/scenarios for that table
- Ensure NO DUPLICATES across all tables

## 📝 OUTPUT FORMAT:

Return ONLY a valid JSON object with this exact structure:
```json
{{
  "business_rules": [
    {{
      "table_name": "table_name",
      "rule_name": "unique_rule_name_1",
      "rule_type": "rule_type",
      "description": "unique_description_1",
      "validation_logic": "validation_logic",
      "error_message": "error_message",
      "severity": "severity",
      "is_active": 1
    }},
    {{
      "table_name": "different_table_name",
      "rule_name": "unique_rule_name_2",
      "rule_type": "different_rule_type",
      "description": "unique_description_2",
      "validation_logic": "different_validation_logic",
      "error_message": "different_error_message",
      "severity": "severity",
      "is_active": 1
    }}
  ],
  "test_scenarios": [
    {{
      "table_name": "table_name",
      "scenario_name": "unique_scenario_name_1",
      "scenario_type": "scenario_type",
      "description": "unique_description_1",
      "test_conditions": "test_conditions",
      "expected_behavior": "expected_behavior",
      "data_requirements": "data_requirements",
      "priority": "priority",
      "is_active": 1
    }},
    {{
      "table_name": "different_table_name",
      "scenario_name": "unique_scenario_name_2",
      "scenario_type": "different_scenario_type",
      "description": "unique_description_2",
      "test_conditions": "different_test_conditions",
      "expected_behavior": "different_expected_behavior",
      "data_requirements": "different_data_requirements",
      "priority": "priority",
      "is_active": 1
    }}
  ]
}}
```

IMPORTANT: 
- Return EXACTLY 3-5 business rules and 3-5 test scenarios TOTAL
- Each rule and scenario must be UNIQUE and different from others
- Distribute across different tables evenly
- Return ONLY the JSON object, no additional text or explanations"""
    
    def generate_from_prompt(self, user_prompt, table_name):
        """Generate ONE business rule OR test scenario from natural language prompt with DATA ANALYSIS."""
        try:
            logger.info(f"🔍 Generating from prompt for table: {table_name} with DATA ANALYSIS")
            
            # STEP 1: Load and analyze the actual data from the table
            input_data = self.load_input_data()
            if not input_data or table_name not in input_data:
                logger.error(f"❌ No data found for table: {table_name}")
                return [], []
            
            table_data = input_data[table_name]
            logger.info(f"📊 Loaded {len(table_data)} records from {table_name}")
            
            # STEP 2: Perform data analysis to understand business context
            data_analysis = self.analyze_table_data(table_data, table_name)
            logger.info(f"🔍 Data analysis completed for {table_name}")
            
            # STEP 3: Load existing library for context
            existing_rules, existing_scenarios = self.load_existing_library()
            existing_context = self.create_existing_context(existing_rules, existing_scenarios, table_name)
            
            # STEP 4: Create enhanced prompt with data analysis context
            enhanced_prompt = self.create_enhanced_llm_prompt(user_prompt, table_name, data_analysis, existing_context)
            
            # STEP 5: Call OpenAI API with data-driven context
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an EXPERT business analyst specializing in FINANCIAL SYSTEMS. Your task is to analyze the provided DATA and generate intelligent business rules and test scenarios.

CRITICAL REQUIREMENTS:
1. ANALYZE the provided data patterns, distributions, and relationships
2. UNDERSTAND the business context from the actual data
3. Generate business rules that are SPECIFIC to the data patterns you observe
4. Create test scenarios that test REAL business logic found in the data
5. Use the data analysis to identify business rules and edge cases
6. Consider cross-table relationships and referential integrity
7. Focus on COMPLEX BUSINESS LOGIC, not just simple validation

DECISION LOGIC:
- If the user describes a validation rule → Generate a BUSINESS RULE based on data analysis
- If the user describes a test case → Generate a TEST SCENARIO based on data analysis
- ALWAYS use the data analysis to inform your business logic generation

OUTPUT FORMAT:
Return a JSON object with either "business_rules" OR "test_scenarios" array (not both)
Each item should be SPECIFIC to the data patterns you analyzed."""
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                max_tokens=3000,
                temperature=0.1
            )
            
            # STEP 6: Parse and validate response
            content = response.choices[0].message.content
            logger.info(f"🤖 AI response received: {len(content)} characters")
            
            # Extract JSON from response with fallback methods
            try:
                # Method 1: Look for JSON content
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_content = content[start_idx:end_idx]
                    result = json.loads(json_content)
                    
                    business_rules = result.get('business_rules', [])
                    test_scenarios = result.get('test_scenarios', [])
                    
                    logger.info(f"✅ Successfully parsed AI response: {len(business_rules)} business rules, {len(test_scenarios)} test scenarios")
                    
                    # Return only one item (prefer test scenario if both exist)
                    if test_scenarios:
                        return [], test_scenarios[:1]  # Return only first test scenario
                    elif business_rules:
                        return business_rules[:1], []  # Return only first business rule
                    else:
                        return [], []
                else:
                    logger.error("❌ No JSON content found in AI response")
                    return [], []
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse AI response as JSON: {str(e)}")
                logger.error(f"Response content: {content}")
                return [], []
            
        except Exception as e:
            logger.error(f"❌ Error generating from prompt with data analysis: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return [], []
    
    def create_existing_context(self, existing_rules, existing_scenarios, table_name):
        """Create context from existing library for the specific table."""
        table_rules = [rule for rule in existing_rules if rule.get('table_name') == table_name]
        table_scenarios = [scenario for scenario in existing_scenarios if scenario.get('table_name') == table_name]
        
        context = f"EXISTING BUSINESS RULES FOR {table_name}:\n"
        for rule in table_rules[:5]:  # Show first 5 rules
            context += f"- {rule.get('rule_name')}: {rule.get('description')}\n"
        
        context += f"\nEXISTING TEST SCENARIOS FOR {table_name}:\n"
        for scenario in table_scenarios[:5]:  # Show first 5 scenarios
            context += f"- {scenario.get('scenario_name')}: {scenario.get('description')}\n"
        
        return context
    
    def create_enhanced_llm_prompt(self, user_prompt, table_name, data_analysis, existing_context):
        """Create enhanced prompt with data analysis context for intelligent business logic generation."""
        return f"""
USER REQUEST: {user_prompt}
TARGET TABLE: {table_name}

## 📊 DATA ANALYSIS RESULTS:
{json.dumps(data_analysis, indent=2)}

## 📚 EXISTING LIBRARY CONTEXT:
{existing_context}

## 🎯 BUSINESS LOGIC GENERATION TASK:

Based on the ACTUAL DATA ANALYSIS above, generate intelligent business rules or test scenarios that:

1. **Use the data patterns you observed** (min/max values, distributions, relationships)
2. **Address the business patterns identified** (age rules, income validation, status rules, etc.)
3. **Consider cross-table relationships** found in the data
4. **Address data quality issues** identified in the analysis
5. **Create business logic specific to the actual data structure**

## 📋 OUTPUT FORMAT:

Return ONLY a valid JSON object with this exact structure:
```json
{{
  "business_rules": [
    {{
      "table_name": "{table_name}",
      "rule_name": "rule_name",
      "rule_type": "rule_type",
      "description": "description",
      "validation_logic": "validation_logic",
      "error_message": "error_message",
      "severity": "severity",
      "is_active": 1
    }}
  ],
  "test_scenarios": [
    {{
      "table_name": "{table_name}",
      "scenario_name": "scenario_name",
      "scenario_type": "scenario_type",
      "description": "description",
      "test_conditions": "test_conditions",
      "expected_behavior": "expected_behavior",
      "data_requirements": "data_requirements",
      "priority": "priority",
      "is_active": 1
    }}
  ]
}}
```

IMPORTANT: 
- Return ONLY the JSON object, no additional text
- Use the data analysis to create SPECIFIC and RELEVANT business logic
- Base your rules/scenarios on the actual data patterns you observed
"""

    def create_llm_prompt(self, user_prompt, table_name, existing_context):
        """Create the prompt for the LLM."""
        return f"""
USER REQUEST: {user_prompt}
TARGET TABLE: {table_name}

{existing_context}

AVAILABLE TABLES: credit_card_accounts, credit_card_products, credit_card_transactions, customer_info, imobile_user_session

CSV FORMAT REQUIREMENTS:

BUSINESS RULES CSV COLUMNS:
- table_name: The table this rule applies to
- rule_name: Descriptive name for the rule
- rule_type: One of [uniqueness, referential, range, enumeration, business_logic]
- description: Clear description of what the rule validates
- validation_logic: Descriptive validation logic (e.g., "field must be unique", "field >= 0", "field IN ('A', 'B')", "field must exist in other_table")
- error_message: Error message when rule is violated
- severity: One of [CRITICAL, HIGH, MEDIUM, LOW]
- is_active: 1 for active rules

TEST SCENARIOS CSV COLUMNS:
- table_name: The table this scenario tests
- scenario_name: Descriptive name for the scenario
- scenario_type: One of [positive, negative, edge_case]
- description: Clear description of the test scenario
- test_conditions: Conditions that must be met
- expected_behavior: Expected outcome when scenario is executed
- data_requirements: Specific data requirements for testing
- priority: One of [HIGH, MEDIUM, LOW, CRITICAL]
- is_active: 1 for active scenarios

Generate BOTH business rules AND test scenarios based on the user's request. Consider:
1. What business rules are needed to enforce the requirements?
2. What test scenarios (positive, negative, edge cases) should be created?
3. How do these relate to existing rules and scenarios?
4. What cross-table relationships might be involved?

Return a JSON object with "business_rules" and "test_scenarios" arrays.
"""
    
    def append_to_library(self, business_rules, test_scenarios):
        """Append new business rules and test scenarios to the library."""
        try:
            logger.info(f"🔄 Starting library append: {len(business_rules)} business rules, {len(test_scenarios)} test scenarios")
            
            # Append business rules
            if business_rules:
                logger.info(f"📝 Appending {len(business_rules)} business rules to {self.business_rules_file}")
                with open(self.business_rules_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['table_name', 'rule_name', 'rule_type', 'description', 'validation_logic', 'error_message', 'severity', 'is_active'])
                    for rule in business_rules:
                        # Ensure all fields are properly escaped and formatted
                        row = {
                            'table_name': str(rule.get('table_name', '')),
                            'rule_name': str(rule.get('rule_name', '')),
                            'rule_type': str(rule.get('rule_type', '')),
                            'description': str(rule.get('description', '')),
                            'validation_logic': str(rule.get('validation_logic', '')),
                            'error_message': str(rule.get('error_message', '')),
                            'severity': str(rule.get('severity', '')),
                            'is_active': str(rule.get('is_active', '1'))
                        }
                        writer.writerow(row)
                logger.info(f"✅ Added {len(business_rules)} business rules to library")
            
            # Append test scenarios
            if test_scenarios:
                logger.info(f"📝 Appending {len(test_scenarios)} test scenarios to {self.test_scenarios_file}")
                with open(self.test_scenarios_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['table_name', 'scenario_name', 'scenario_type', 'description', 'test_conditions', 'expected_behavior', 'data_requirements', 'priority', 'is_active'])
                    for scenario in test_scenarios:
                        # Ensure all fields are properly escaped and formatted
                        row = {
                            'table_name': str(scenario.get('table_name', '')),
                            'scenario_name': str(scenario.get('scenario_name', '')),
                            'description': str(scenario.get('description', '')),
                            'scenario_type': str(scenario.get('scenario_type', '')),
                            'test_conditions': str(scenario.get('test_conditions', '')),
                            'expected_behavior': str(scenario.get('expected_behavior', '')),
                            'data_requirements': str(scenario.get('data_requirements', '')),
                            'priority': str(scenario.get('priority', '')),
                            'is_active': str(scenario.get('is_active', '1'))
                        }
                        writer.writerow(row)
                logger.info(f"✅ Added {len(test_scenarios)} test scenarios to library")
            
            # Also update the run's schema analysis if run_id is provided
            if self.run_id:
                logger.info(f"🔄 Updating run {self.run_id} schema analysis with generated content")
                self.update_run_schema_analysis(business_rules, test_scenarios)
            
            logger.info(f"🎉 Library append completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error appending to library: {str(e)}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def update_run_schema_analysis(self, business_rules, test_scenarios):
        """Update the run's schema analysis with new business rules and test scenarios."""
        try:
            if not self.run_id:
                return
            
            schema_file = os.path.join(self.schema_dir, "schema_analysis_results.json")
            if not os.path.exists(schema_file):
                logger.warning(f"Schema analysis file not found: {schema_file}")
                return
            
            # Load existing schema analysis
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_analysis = json.load(f)
            
            # Update business rules
            if business_rules:
                for rule in business_rules:
                    table_name = rule.get('table_name')
                    if table_name:
                        # Find the table in schema analysis
                        for table in schema_analysis.get('tables', []):
                            if table.get('table_name') == table_name:
                                if 'business_rules' not in table:
                                    table['business_rules'] = []
                                
                                # Convert CSV format to schema analysis format
                                new_rule = {
                                    'rule_name': rule.get('rule_name'),
                                    'description': rule.get('description'),
                                    'validation_logic': rule.get('validation_logic'),
                                    'error_message': rule.get('error_message')
                                }
                                table['business_rules'].append(new_rule)
                                logger.info(f"Added business rule '{rule.get('rule_name')}' to {table_name} in run schema")
                                break
            
            # Update test scenarios
            if test_scenarios:
                for scenario in test_scenarios:
                    table_name = scenario.get('table_name')
                    if table_name:
                        # Find the table in schema analysis
                        for table in schema_analysis.get('tables', []):
                            if table.get('table_name') == table_name:
                                if 'test_scenarios' not in table:
                                    table['test_scenarios'] = []
                                
                                # Convert CSV format to schema analysis format
                                new_scenario = {
                                    'scenario_name': scenario.get('scenario_name'),
                                    'description': scenario.get('description'),
                                    'test_type': scenario.get('scenario_type'),
                                    'business_logic': scenario.get('test_conditions'),
                                    'expected_behavior': scenario.get('expected_behavior'),
                                    'data_requirements': {
                                        'field_name': 'nationality',
                                        'constraints': scenario.get('data_requirements'),
                                        'sample_values': ['Indian']
                                    }
                                }
                                table['test_scenarios'].append(new_scenario)
                                logger.info(f"Added test scenario '{scenario.get('scenario_name')}' to {table_name} in run schema")
                                break
            
            # Save updated schema analysis
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema_analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated run {self.run_id} schema analysis with new business rules and test scenarios")
            
        except Exception as e:
            logger.error(f"Error updating run schema analysis: {str(e)}")
    
    def display_library_summary(self):
        """Display a summary of the current library."""
        business_rules, test_scenarios = self.load_existing_library()
        
        print("\n" + "="*60)
        print("BUSINESS LOGIC LIBRARY SUMMARY")
        print("="*60)
        
        # Count by table
        table_counts = {}
        for rule in business_rules:
            table = rule.get('table_name', 'Unknown')
            if table not in table_counts:
                table_counts[table] = {'rules': 0, 'scenarios': 0}
            table_counts[table]['rules'] += 1
        
        for scenario in test_scenarios:
            table = scenario.get('table_name', 'Unknown')
            if table not in table_counts:
                table_counts[table] = {'rules': 0, 'scenarios': 0}
            table_counts[table]['scenarios'] += 1
        
        for table, counts in table_counts.items():
            print(f"\n{table}:")
            print(f"  Business Rules: {counts['rules']}")
            print(f"  Test Scenarios: {counts['scenarios']}")
        
        print(f"\nTOTAL:")
        print(f"  Business Rules: {len(business_rules)}")
        print(f"  Test Scenarios: {len(test_scenarios)}")
        print("="*60)
    
    def detect_tables_from_prompt(self, user_prompt):
        """Detect relevant tables from natural language prompt."""
        try:
            # Call OpenAI to detect tables
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at analyzing business requirements and identifying which database tables they affect.

AVAILABLE TABLES:
- credit_card_accounts: Credit card account information, status, limits, balances
- credit_card_products: Credit card product definitions, rates, fees, features
- credit_card_transactions: Transaction records, amounts, status, merchant info
- customer_info: Customer personal information, KYC status, demographics
- imobile_user_session: Mobile banking sessions, authentication, device info

TASK: Analyze the user's business requirement and identify which tables are relevant.

OUTPUT: Return a JSON array of table names that are affected by this requirement.
Example: ["credit_card_accounts", "credit_card_transactions"]"""
                    },
                    {
                        "role": "user",
                        "content": f"Business requirement: {user_prompt}"
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                json_str = content[start:end].strip()
            else:
                json_str = content
            
            tables = json.loads(json_str)
            
            # Validate tables
            valid_tables = ['credit_card_accounts', 'credit_card_products', 'credit_card_transactions', 'customer_info', 'imobile_user_session']
            tables = [table for table in tables if table in valid_tables]
            
            return tables
            
        except Exception as e:
            logger.error(f"Error detecting tables: {str(e)}")
            return []

    def chat_interface(self):
        """Interactive chat interface for generating business logic."""
        print("\n" + "="*60)
        print("BUSINESS LOGIC LIBRARY GENERATOR")
        print("="*60)
        print("Available tables: credit_card_accounts, credit_card_products, credit_card_transactions, customer_info, imobile_user_session")
        print("Type 'quit' to exit, 'summary' to see library summary")
        print("="*60)
        
        while True:
            try:
                # Get user prompt
                user_prompt = input("\nDescribe the business logic or test scenario: ").strip()
                if user_prompt.lower() == 'quit':
                    break
                elif user_prompt.lower() == 'summary':
                    self.display_library_summary()
                    continue
                
                if not user_prompt:
                    print("Please provide a description.")
                    continue
                
                print(f"\n🔍 Analyzing your requirement...")
                
                # Detect relevant tables
                relevant_tables = self.detect_tables_from_prompt(user_prompt)
                
                if not relevant_tables:
                    print("❌ Could not identify relevant tables from your description.")
                    print("Please be more specific about which tables this affects.")
                    continue
                
                print(f"📋 Detected relevant tables: {', '.join(relevant_tables)}")
                
                # Generate business logic for the first relevant table only
                table_name = relevant_tables[0]  # Use only the first detected table
                print(f"\n🔧 Generating for {table_name}...")
                
                # Generate business logic
                business_rules, test_scenarios = self.generate_from_prompt(user_prompt, table_name)
                
                if not business_rules and not test_scenarios:
                    print("❌ No business logic generated. Please try again with a more specific description.")
                    continue
                
                # Display generated item
                if business_rules:
                    rule = business_rules[0]
                    print(f"\n📋 GENERATED BUSINESS RULE:")
                    print(f"  [{rule.get('table_name')}] {rule.get('rule_name')}")
                    print(f"  Description: {rule.get('description')}")
                    print(f"  Type: {rule.get('rule_type')} | Severity: {rule.get('severity')}")
                    
                    # Automatically append to library
                    success = self.append_to_library(business_rules, [])
                    if success:
                        print("✅ Automatically added business rule to library!")
                    else:
                        print("❌ Failed to add to library.")
                
                elif test_scenarios:
                    scenario = test_scenarios[0]
                    print(f"\n🧪 GENERATED TEST SCENARIO:")
                    print(f"  [{scenario.get('table_name')}] {scenario.get('scenario_name')}")
                    print(f"  Description: {scenario.get('description')}")
                    print(f"  Type: {scenario.get('scenario_type')} | Priority: {scenario.get('priority')}")
                    
                    # Automatically append to library
                    success = self.append_to_library([], test_scenarios)
                    if success:
                        print("✅ Automatically added test scenario to library!")
                    else:
                        print("❌ Failed to add to library.")
                
            except KeyboardInterrupt:
                print("\n\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue

    def run(self):
        """Main execution method based on mode."""
        if self.mode == "data_analysis":
            print(f"\n🤖 AI-Powered Business Logic Generation Engine")
            print(f"📊 Run ID: {self.run_id}")
            print("="*60)
            
            logger.info(f"🚀 Initializing intelligent business logic generation for run: {self.run_id}")
            print("🎯 Mode: Data Analysis - Generating business rules and test scenarios from data analysis...")
            
            success = self.generate_from_data_analysis()
            
            if success:
                logger.info("🎉 Business logic generation completed successfully")
                print("✅ Business logic generation completed successfully!")
                self.display_library_summary()
            else:
                logger.error("❌ Business logic generation failed")
                print("❌ Business logic generation failed.")
                
        else:
            # Interactive mode
            print(f"\n🤖 AI-Powered Business Logic Generation Engine")
            print("🎯 Mode: Interactive Chat")
            print("="*60)
            logger.info("🚀 Initializing interactive business logic generation")
            self.chat_interface()

    def integrate_with_existing_schema_analysis(self, input_data, new_business_rules, new_test_scenarios):
        """Integrate new business logic with existing schema analysis and library."""
        try:
            schema_file = os.path.join(self.schema_dir, "schema_analysis_results.json")
            
            # ALWAYS load business logic from library first
            logger.info("Loading business logic from library...")
            library_business_rules, library_test_scenarios = self.load_existing_library()
            logger.info(f"Loaded {len(library_business_rules)} business rules and {len(library_test_scenarios)} test scenarios from library")
            
            # Select 3-5 business rules and test scenarios per table from library
            curated_library_rules, curated_library_scenarios = self.curate_library_content(library_business_rules, library_test_scenarios, max_per_table=5)
            logger.info(f"Curated {len(curated_library_rules)} business rules and {len(curated_library_scenarios)} test scenarios from library (3-5 per table)")
            
            # Check if existing schema analysis exists
            if os.path.exists(schema_file):
                logger.info("Found existing schema analysis, integrating curated library content and new business logic...")
                
                # Load existing schema analysis
                with open(schema_file, 'r', encoding='utf-8') as f:
                    existing_analysis = json.load(f)
                
                # Integrate curated library business logic first
                updated_analysis = self.merge_business_logic_into_schema(existing_analysis, curated_library_rules, curated_library_scenarios)
                
                # Then integrate new business logic
                updated_analysis = self.merge_business_logic_into_schema(updated_analysis, new_business_rules, new_test_scenarios)
                
                # Save updated analysis
                with open(schema_file, 'w', encoding='utf-8') as f:
                    json.dump(updated_analysis, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Successfully integrated curated library ({len(curated_library_rules)} rules, {len(curated_library_scenarios)} scenarios) and new ({len(new_business_rules)} rules, {len(new_test_scenarios)} scenarios) with existing schema analysis")
                
            else:
                logger.info("No existing schema analysis found, creating new one with curated library integration...")
                # Create new schema analysis that includes curated library data
                self.create_basic_schema_analysis_with_library(input_data, new_business_rules, new_test_scenarios, curated_library_rules, curated_library_scenarios)
                
        except Exception as e:
            logger.error(f"Error integrating with existing schema analysis: {str(e)}")
            # Fall back to creating new schema analysis
            self.create_basic_schema_analysis(input_data, new_business_rules, new_test_scenarios)
    
    def curate_library_content(self, library_business_rules, library_test_scenarios, max_per_table=5):
        """Curate library content to select 3-5 business rules and test scenarios per table."""
        try:
            curated_rules = []
            curated_scenarios = []
            
            # Group by table
            rules_by_table = {}
            scenarios_by_table = {}
            
            for rule in library_business_rules:
                table_name = rule.get('table_name', '')
                if table_name not in rules_by_table:
                    rules_by_table[table_name] = []
                rules_by_table[table_name].append(rule)
            
            for scenario in library_test_scenarios:
                table_name = scenario.get('table_name', '')
                if table_name not in scenarios_by_table:
                    scenarios_by_table[table_name] = []
                scenarios_by_table[table_name].append(scenario)
            
            # Select 3-5 items per table, prioritizing by severity/priority
            for table_name in set(list(rules_by_table.keys()) + list(scenarios_by_table.keys())):
                # Select business rules for this table
                if table_name in rules_by_table:
                    table_rules = rules_by_table[table_name]
                    # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW)
                    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                    table_rules.sort(key=lambda x: severity_order.get(x.get('severity', 'MEDIUM'), 2))
                    
                    # Select up to max_per_table rules
                    selected_rules = table_rules[:max_per_table]
                    curated_rules.extend(selected_rules)
                    logger.info(f"Selected {len(selected_rules)} business rules for {table_name}")
                
                # Select test scenarios for this table
                if table_name in scenarios_by_table:
                    table_scenarios = scenarios_by_table[table_name]
                    # Sort by priority (CRITICAL > HIGH > MEDIUM > LOW)
                    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                    table_scenarios.sort(key=lambda x: priority_order.get(x.get('priority', 'MEDIUM'), 2))
                    
                    # Select up to max_per_table scenarios
                    selected_scenarios = table_scenarios[:max_per_table]
                    curated_scenarios.extend(selected_scenarios)
                    logger.info(f"Selected {len(selected_scenarios)} test scenarios for {table_name}")
            
            logger.info(f"Curated library content: {len(curated_rules)} business rules, {len(curated_scenarios)} test scenarios")
            return curated_rules, curated_scenarios
            
        except Exception as e:
            logger.error(f"Error curating library content: {str(e)}")
            # Return original content if curation fails
            return library_business_rules, library_test_scenarios
    
    def merge_business_logic_into_schema(self, existing_analysis, new_business_rules, new_test_scenarios):
        """Merge new business logic into existing schema analysis."""
        try:
            if "tables" not in existing_analysis:
                return existing_analysis
            
            # Group new business logic by table
            new_rules_by_table = {}
            new_scenarios_by_table = {}
            
            for rule in new_business_rules:
                table_name = rule.get('table_name', '')
                if table_name not in new_rules_by_table:
                    new_rules_by_table[table_name] = []
                new_rules_by_table[table_name].append(rule)
            
            for scenario in new_test_scenarios:
                table_name = scenario.get('table_name', '')
                if table_name not in new_scenarios_by_table:
                    new_scenarios_by_table[table_name] = []
                new_scenarios_by_table[table_name].append(scenario)
            
            # Merge into existing tables
            for table in existing_analysis["tables"]:
                table_name = table.get('table_name', '')
                
                # Initialize arrays if they don't exist
                if "business_rules" not in table:
                    table["business_rules"] = []
                if "test_scenarios" not in table:
                    table["test_scenarios"] = []
                
                # Add new business rules
                if table_name in new_rules_by_table:
                    for rule in new_rules_by_table[table_name]:
                        # Check for duplicates before adding
                        rule_exists = any(
                            existing_rule.get('rule_name') == rule.get('rule_name') and
                            existing_rule.get('description') == rule.get('description')
                            for existing_rule in table["business_rules"]
                        )
                        
                        if not rule_exists:
                            table["business_rules"].append({
                                "rule_name": rule.get('rule_name'),
                                "description": rule.get('description'),
                                "validation_logic": rule.get('validation_logic'),
                                "error_message": rule.get('error_message'),
                                "rule_type": rule.get('rule_type', 'business_logic'),
                                "severity": rule.get('severity', 'MEDIUM')
                            })
                            logger.info(f"Added new business rule '{rule.get('rule_name')}' to {table_name}")
                
                # Add new test scenarios
                if table_name in new_scenarios_by_table:
                    for scenario in new_scenarios_by_table[table_name]:
                        # Check for duplicates before adding
                        scenario_exists = any(
                            existing_scenario.get('scenario_name') == scenario.get('scenario_name') and
                            existing_scenario.get('description') == scenario.get('description')
                            for existing_scenario in table["test_scenarios"]
                        )
                        
                        if not scenario_exists:
                            table["test_scenarios"].append({
                                "scenario_name": scenario.get('scenario_name'),
                                "description": scenario.get('description'),
                                "test_type": scenario.get('scenario_type'),
                                "business_logic": scenario.get('test_conditions'),
                                "expected_behavior": scenario.get('expected_behavior'),
                                "data_requirements": scenario.get('data_requirements'),
                                "priority": scenario.get('priority', 'MEDIUM')
                            })
                            logger.info(f"Added new test scenario '{scenario.get('scenario_name')}' to {table_name}")
            
            logger.info(f"Successfully merged {len(new_business_rules)} business rules and {len(new_test_scenarios)} test scenarios into existing schema")
            return existing_analysis
            
        except Exception as e:
            logger.error(f"Error merging business logic into schema: {str(e)}")
            return existing_analysis
    
    def create_basic_schema_analysis_with_library(self, input_data, new_business_rules, new_test_scenarios, library_business_rules, library_test_scenarios):
        """Create a new schema analysis that includes curated library business logic."""
        try:
            if not self.run_id:
                return
            
            # Apply our improved deduplication and minimum count system
            logger.info("Applying deduplication and minimum count to schema analysis...")
            unique_business_rules, unique_test_scenarios = self.deduplicate_business_logic(new_business_rules, new_test_scenarios)
            final_business_rules, final_test_scenarios = self.ensure_minimum_count(unique_business_rules, unique_test_scenarios, target_min=3)
            
            logger.info(f"Schema analysis: {len(final_business_rules)} new business rules, {len(final_test_scenarios)} new test scenarios")
            logger.info(f"Library integration: {len(library_business_rules)} curated business rules, {len(library_test_scenarios)} curated test scenarios")
            
            # Ensure the schema directory exists
            os.makedirs(self.schema_dir, exist_ok=True)
            
            schema_file = os.path.join(self.schema_dir, "schema_analysis_results.json")
            
            # Create basic schema analysis structure
            schema_analysis = {
                "run_id": self.run_id,
                "generated_at": datetime.now().isoformat(),
                "mode": "data_analysis_with_curated_library",
                "tables": [],
                "cross_table_relationships": self.validate_cross_table_relationships([
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
                ])
            }
            
            # If input_data is empty, create basic table structure from library data
            if not input_data:
                logger.info("No input data provided, creating basic table structure from curated library data...")
                table_names = set()
                
                # Extract table names from library data
                for rule in library_business_rules:
                    table_names.add(rule.get('table_name', ''))
                for scenario in library_test_scenarios:
                    table_names.add(scenario.get('table_name', ''))
                
                # Remove empty table names
                table_names.discard('')
                
                # Create basic table structure
                for table_name in table_names:
                    table_info = {
                        "table_name": table_name,
                        "record_count": 0,
                        "columns": [],
                        "business_rules": [],
                        "test_scenarios": [],
                        "data_generation_rules": []
                    }
                    
                    # Add curated library business rules for this table
                    for rule in library_business_rules:
                        if rule.get('table_name') == table_name:
                            table_info["business_rules"].append({
                                "rule_name": rule.get('rule_name'),
                                "description": rule.get('description'),
                                "validation_logic": rule.get('validation_logic'),
                                "error_message": rule.get('error_message'),
                                "rule_type": rule.get('rule_type', 'business_logic'),
                                "severity": rule.get('severity', 'MEDIUM'),
                                "source": "curated_library"
                            })
                    
                    # Add curated library test scenarios for this table
                    for scenario in library_test_scenarios:
                        if scenario.get('table_name') == table_name:
                            table_info["test_scenarios"].append({
                                "scenario_name": scenario.get('scenario_name'),
                                "description": scenario.get('description'),
                                "test_type": scenario.get('scenario_type'),
                                "business_logic": scenario.get('test_conditions'),
                                "expected_behavior": scenario.get('expected_behavior'),
                                "data_requirements": scenario.get('data_requirements'),
                                "priority": scenario.get('priority', 'MEDIUM'),
                                "source": "curated_library"
                            })
                    
                    # Add new business rules for this table (already deduplicated and with minimum count)
                    for rule in final_business_rules:
                        if rule.get('table_name') == table_name:
                            table_info["business_rules"].append({
                                "rule_name": rule.get('rule_name'),
                                "description": rule.get('description'),
                                "validation_logic": rule.get('validation_logic'),
                                "error_message": rule.get('error_message'),
                                "rule_type": rule.get('rule_type', 'business_logic'),
                                "severity": rule.get('severity', 'MEDIUM'),
                                "source": "new_generation"
                            })
                    
                    # Add new test scenarios for this table (already deduplicated and with minimum count)
                    for scenario in final_test_scenarios:
                        if scenario.get('table_name') == table_name:
                            table_info["test_scenarios"].append({
                                "scenario_name": scenario.get('scenario_name'),
                                "description": scenario.get('description'),
                                "test_type": scenario.get('scenario_type'),
                                "business_logic": scenario.get('test_conditions'),
                                "expected_behavior": scenario.get('expected_behavior'),
                                "data_requirements": scenario.get('data_requirements'),
                                "priority": scenario.get('priority', 'MEDIUM'),
                                "source": "new_generation"
                            })
                    
                    # Add the table info to the schema analysis
                    schema_analysis["tables"].append(table_info)
            else:
                # Original logic for when input_data is provided
                for table_name, df in input_data.items():
                    table_info = {
                        "table_name": table_name,
                        "record_count": int(len(df)),
                        "columns": [],
                        "business_rules": [],
                        "test_scenarios": [],
                        "data_generation_rules": []
                    }
                    
                    # Add column information
                    for col in df.columns:
                        col_info = {
                            "column_name": col,
                            "data_type": str(df[col].dtype),
                            "is_nullable": bool(df[col].isna().any()),
                            "unique_values": int(df[col].nunique()) if df[col].dtype == 'object' else None,
                            "min_value": float(df[col].min()) if df[col].dtype in ['int64', 'float64'] and pd.notna(df[col].min()) else None,
                            "max_value": float(df[col].max()) if df[col].dtype in ['int64', 'float64'] and pd.notna(df[col].max()) else None
                        }
                        table_info["columns"].append(col_info)
                    
                    # Add curated library business rules for this table
                    for rule in library_business_rules:
                        if rule.get('table_name') == table_name:
                            table_info["business_rules"].append({
                                "rule_name": rule.get('rule_name'),
                                "description": rule.get('description'),
                                "validation_logic": rule.get('validation_logic'),
                                "error_message": rule.get('error_message'),
                                "rule_type": rule.get('rule_type', 'business_logic'),
                                "severity": rule.get('severity', 'MEDIUM'),
                                "source": "curated_library"
                            })
                    
                    # Add curated library test scenarios for this table
                    for scenario in library_test_scenarios:
                        if scenario.get('table_name') == table_name:
                            table_info["test_scenarios"].append({
                                "scenario_name": scenario.get('scenario_name'),
                                "description": scenario.get('description'),
                                "test_type": scenario.get('scenario_type'),
                                "business_logic": scenario.get('test_conditions'),
                                "expected_behavior": scenario.get('expected_behavior'),
                                "data_requirements": scenario.get('data_requirements'),
                                "priority": scenario.get('priority', 'MEDIUM'),
                                "source": "curated_library"
                            })
                    
                    # Add new business rules for this table (already deduplicated and with minimum count)
                    for rule in final_business_rules:
                        if rule.get('table_name') == table_name:
                            table_info["business_rules"].append({
                                "rule_name": rule.get('rule_name'),
                                "description": rule.get('description'),
                                "validation_logic": rule.get('validation_logic'),
                                "error_message": rule.get('error_message'),
                                "rule_type": rule.get('rule_type', 'business_logic'),
                                "severity": rule.get('severity', 'MEDIUM'),
                                "source": "new_generation"
                            })
                    
                    # Add new test scenarios for this table (already deduplicated and with minimum count)
                    for scenario in final_test_scenarios:
                        if scenario.get('table_name') == table_name:
                            table_info["test_scenarios"].append({
                                "scenario_name": scenario.get('scenario_name'),
                                "description": scenario.get('description'),
                                "test_type": scenario.get('scenario_type'),
                                "business_logic": scenario.get('test_conditions'),
                                "expected_behavior": scenario.get('expected_behavior'),
                                "data_requirements": scenario.get('data_requirements'),
                                "priority": scenario.get('priority', 'MEDIUM'),
                                "source": "new_generation"
                            })
                    
                    # Add the table info to the schema analysis
                    schema_analysis["tables"].append(table_info)
            
            # Save the schema analysis
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema_analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created new schema analysis with curated library integration: {schema_file}")
            logger.info(f"Total business rules: {sum(len(table['business_rules']) for table in schema_analysis['tables'])}")
            logger.info(f"Total test scenarios: {sum(len(table['test_scenarios']) for table in schema_analysis['tables'])}")
            
        except Exception as e:
            logger.error(f"Error creating schema analysis with library: {str(e)}")
            # Fall back to basic creation
            self.create_basic_schema_analysis(input_data, new_business_rules, new_test_scenarios)

def main():
    """Main function to run the library generator agent."""
    print("🔧 Business Logic Library Generator")
    print("="*50)
    print("Select mode:")
    print("1. Interactive mode (chat-based generation)")
    print("2. Data analysis mode (from existing run)")
    
    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == "1":
            mode = "interactive"
            # Ask if user wants to specify a run ID for updating schema analysis
            use_run_id = input("Do you want to update a specific run's schema analysis? (y/n): ").strip().lower()
            if use_run_id in ['y', 'yes']:
                run_id = input("Enter run ID: ").strip()
                if not run_id:
                    print("No run ID provided. Will only update library files.")
                    run_id = None
            else:
                run_id = None
            break
        elif choice == "2":
            mode = "data_analysis"
            run_id = input("Enter run ID: ").strip()
            if not run_id:
                print("Run ID is required for data analysis mode.")
                continue
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    agent = LibraryGeneratorAgent(run_id=run_id, mode=mode)
    agent.run()

if __name__ == "__main__":
    main() 