# Test Data Environment - Backend

A sophisticated AI-powered synthetic data generation and validation system designed for financial/banking applications. This system creates realistic test data for credit card systems while ensuring business rule compliance and comprehensive test coverage.

## 🏗️ New Folder Structure

The system now uses a unique folder structure for each run, ensuring clean separation and organization:

```
runs/
├── 20241201_143022/                    # Unique run ID (YYYYMMDD_HHMMSS)
│   ├── input_data/                     # Input data files (Functional Test Scenario Generation)
│   ├── schema/                         # Schema analysis results
│   │   └── schema_analysis_results.json
│   ├── synthetic_data/                 # Generated synthetic data (Synthetic Data Generation)
│   │   ├── customer_info.csv
│   │   ├── credit_card_accounts.csv
│   │   ├── credit_card_products.csv
│   │   ├── credit_card_transactions.csv
│   │   ├── imobile_user_session.csv
│   │   └── generated_data_generator.py
│   └── validation/                     # Validation results
│       ├── validation_report.json
│       ├── validation_summary.txt
│       └── generated_validator.py
├── 20241201_150145/                    # Another run
│   └── ...
└── ...
```

## 🎯 Two User Journeys

The system supports two distinct user journeys:

### **Synthetic Data Generation: Schema-Only → Full Pipeline**
**Input**: Schema files only (`input_schemas/`)
**Workflow**:
1. **Schema Analysis** (with test scenarios and business logic generation)
2. **Synthetic Data Generation** (creates realistic test data)
3. **Validation** (validates generated data)
4. **Test Scenario Generation** (optional - adds specific test cases)

**Use Case**: When you have schema definitions but no existing data, and want to generate comprehensive test data from scratch.

### **Functional Test Scenario Generation: Data + Schema → Business Logic → Test Scenarios**
**Input**: Schema files + existing data files (`input_schemas/` + `runs/{run_id}/input_data/`)
**Workflow**:
1. **Schema Analysis** (schema structure only, no test scenarios)
2. **Business Logic Generation** (analyzes existing data to create business rules)
3. **Test Scenario Generation** (creates test scenarios based on business logic)
4. **Validation** (validates existing data against new rules)

**Use Case**: When you have existing data and want to analyze it to create business rules and test scenarios for validation.

## 🚀 Quick Start

### Option 1: Run Complete Pipeline (Recommended)

Run the entire pipeline with journey selection:

```bash
python run_complete_pipeline.py
```

This will:
1. Ask you to select a user journey (1 or 2)
2. Create a unique run folder with timestamp
3. Execute the appropriate workflow for your journey
4. Generate comprehensive outputs and reports

### Option 2: Run Individual Agents

You can also run each agent individually:

```bash
# Schema Analysis (with mode selection)
python schema_analyzer_agent.py

# Synthetic Data Generation
python synthetic_data_generator_agent.py

# Business Logic Generation (Functional Test Scenario Generation)
python business_logic_library/library_generator_agent.py

# Validation
python validation_agent.py

# Test Scenario Data Generation
python test_scenario_data_generator_agent.py
```

## 🔧 Environment Configuration

### **Setup Environment Variables**

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Configure your settings** in `.env`:
   ```bash
   # OpenAI Configuration
   OPENAI_API_KEY=your-actual-openai-api-key
   
   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   ENVIRONMENT=development
   
   # CORS Configuration
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
   
   # Database Configuration (if needed)
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_DATABASE=test_data_environment
   MYSQL_USERNAME=root
   MYSQL_PASSWORD=your-password
   ```

3. **Start the backend**:
   ```bash
   python start_backend.py
   ```

### **Production Deployment**

For production deployment (e.g., on Render), set environment variables in your deployment platform:

- Set `ENVIRONMENT=production`
- Configure `ALLOWED_ORIGINS` with your frontend domain
- Set all required database credentials
- Never commit `.env` files to version control

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📋 System Components

### 1. Schema Analysis Agent
- **Purpose**: Analyzes CSV schema files to understand data structure and relationships
- **Input**: `input_schemas/` directory
- **Output**: `runs/{run_id}/schema/schema_analysis_results.json`
- **Modes**:
  - **Full Mode** (Synthetic Data Generation): Generates test scenarios and business logic
  - **Schema-Only Mode** (Functional Test Scenario Generation): Analyzes schema structure only
- **Functionality**:
  - Identifies primary keys for each table
  - Discovers business rules and constraints (full mode)
  - Generates test scenarios (full mode)
  - Maps cross-table relationships
  - Provides data generation recommendations

### 2. Synthetic Data Generator Agent
- **Purpose**: Generates realistic synthetic data based on schema analysis
- **Input**: Schema analysis results (full mode)
- **Output**: `runs/{run_id}/synthetic_data/` (CSV files + generator code)
- **Journey**: Synthetic Data Generation only
- **Functionality**:
  - Implements dependency resolution (generates data in correct order)
  - Applies business rules during generation
  - Injects test scenarios according to specified mix
  - Ensures referential integrity across tables

### 3. Business Logic Library Generator Agent
- **Purpose**: Generates business rules and test scenarios
- **Input**: Schema analysis + existing data (Functional Test Scenario Generation) OR natural language prompts (interactive)
- **Output**: `business_logic_library/` (CSV files)
- **Modes**:
  - **Data Analysis Mode** (Functional Test Scenario Generation): Analyzes existing data to generate rules
  - **Interactive Mode**: Chat-based generation from natural language
- **Functionality**:
  - Analyzes existing data patterns and distributions
  - Generates business rules based on data analysis
  - Creates test scenarios for validation
  - Interactive chat interface for manual rule creation

### 4. Validation Agent
- **Purpose**: Validates data against business rules and test scenarios
- **Input**: Generated synthetic data (Synthetic Data Generation) OR existing data (Functional Test Scenario Generation) + schema analysis
- **Output**: `runs/{run_id}/validation/` (validation reports)
- **Functionality**:
  - Validates business rule compliance
  - Tests scenario implementation
  - Checks cross-table relationships
  - Generates detailed validation reports

### 5. Test Scenario Data Generator Agent
- **Purpose**: Generates additional test data for specific scenarios
- **Input**: Business logic library + existing synthetic data
- **Output**: Appends to existing synthetic data files
- **Functionality**:
  - Interactive selection of test scenarios
  - Generates data for specific test cases
  - Maintains referential integrity
  - Configurable record counts and priority multipliers

### 6. Business Logic Library
- **Location**: `business_logic_library/`
- **Components**:
  - `business_rules.csv`: 35+ validation rules
  - `test_scenarios.csv`: 135+ test scenarios
  - `library_generator_agent.py`: Interactive chat agent for adding new rules

## 📊 Data Model

The system handles **5 core tables**:

1. **`customer_info`**: Customer demographics, KYC status, income
2. **`credit_card_products`**: Product definitions, rates, fees
3. **`credit_card_accounts`**: Account details, limits, balances, status
4. **`credit_card_transactions`**: Transaction records, amounts, merchant info
5. **`imobile_user_session`**: Mobile banking sessions, authentication

## 🔧 Configuration

### Environment Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure OpenAI API key in `config.py`:
   ```python
   OPENAI_API_KEY = "your-openai-api-key-here"
   ```

### Data Generation Configuration
The system supports configurable data volumes and distributions:

```python
config = {
    "volume_percentage": 0.05,  # Generate 5% of recommended volumes
    "volume_overrides": {
        "customer_info": 500,
        "credit_card_accounts": 750,
        "credit_card_products": 10,
        "credit_card_transactions": 2500,
        "imobile_user_session": 2500
    },
    "scenario_mix": {
        "positive": 0.7,      # 70% positive scenarios
        "negative": 0.2,      # 20% negative scenarios
        "edge_case": 0.1      # 10% edge cases
    },
    "output_format": "csv",
    "seed": 42               # For reproducible generation
}
```

## 📈 Business Rules & Test Scenarios

### Business Rules (35+ rules)
- **Uniqueness**: Primary key constraints
- **Referential**: Foreign key relationships
- **Range**: Value range validations
- **Enumeration**: Valid value sets
- **Business Logic**: Complex business constraints

### Test Scenarios (135+ scenarios)
- **Positive**: Normal, expected behavior (70%)
- **Negative**: Error conditions (20%)
- **Edge Cases**: Boundary conditions (10%)

## 🎯 Key Features

### AI-Powered Generation
- Uses OpenAI GPT-4 for intelligent code generation
- Natural language business logic creation
- Automatic schema analysis and relationship detection
- Dynamic validation code generation

### Data Quality Assurance
- Referential integrity across tables
- Business rule enforcement during generation
- Comprehensive validation reporting
- Data quality metrics and statistics

### Unique Run Management
- Each run creates a unique folder with timestamp
- Complete isolation between runs
- Organized output structure
- Easy comparison between different runs

### Interactive Business Logic Management
- Chat-based interface for adding new rules
- Automatic rule categorization
- Test scenario generation from natural language
- Library of reusable business logic

### Dual Journey Support
- **Synthetic Data Generation**: Schema-only to full synthetic data generation
- **Functional Test Scenario Generation**: Data analysis to business logic and test scenarios
- Flexible workflow selection
- Appropriate outputs for each journey

## 📁 File Structure

```
├── runs/                              # All run outputs
├── input_schemas/                     # Input schema files
├── business_logic_library/            # Business rules and scenarios
├── schema_analyzer_agent.py           # Schema analysis agent
├── synthetic_data_generator_agent.py  # Data generation agent
├── validation_agent.py                # Validation agent
├── test_scenario_data_generator_agent.py  # Test scenario agent
├── business_logic_library/library_generator_agent.py  # Business logic generator
├── run_complete_pipeline.py           # Master orchestrator
├── config.py                          # Configuration
├── requirements.txt                   # Dependencies
└── README.md                          # This file
```

## 🔍 Validation Reports

Each run generates comprehensive validation reports:

- **`validation_report.json`**: Detailed validation results
- **`validation_summary.txt`**: Human-readable summary
- **`generated_validator.py`**: Generated validation code

## 🚨 Error Handling

The system includes robust error handling:
- Graceful failure with detailed error messages
- Logging at multiple levels
- Automatic cleanup of temporary files
- Rollback capabilities for failed runs

## 📝 Usage Examples

### Running Synthetic Data Generation (Schema-Only)
```bash
python run_complete_pipeline.py
# Select Synthetic Data Generation when prompted
# Enter custom run ID when prompted: "synthetic_data_test_001"
```

### Running Functional Test Scenario Generation (Data + Schema)
```bash
# First, place your data files in runs/{run_id}/input_data/
python run_complete_pipeline.py
# Select Functional Test Scenario Generation when prompted
# Enter run ID with existing data: "functional_test_001"
```

### Running Individual Steps
```bash
# Schema analysis with mode selection
python schema_analyzer_agent.py

# Business logic generation from data analysis
python business_logic_library/library_generator_agent.py
# Select mode 2 and enter run ID

# Interactive business logic generation
python business_logic_library/library_generator_agent.py
# Select mode 1 for chat interface
```

### Adding New Business Rules
```bash
python business_logic_library/library_generator_agent.py
# Select mode 1 for interactive mode
# Follow the interactive prompts to add new rules
```

## 🎉 Success Metrics

### Synthetic Data Generation Success Metrics:
- **500 customer records**
- **750 credit card accounts**
- **10 credit card products**
- **2,500+ transactions**
- **2,500+ mobile sessions**
- **100% business rule compliance**
- **Comprehensive test scenario coverage**

### Functional Test Scenario Generation Success Metrics:
- **Schema analysis completed**
- **Business rules generated from data patterns**
- **Test scenarios created for validation**
- **Existing data validated against new rules**
- **Data quality insights generated**

## 🔧 Troubleshooting

### Common Issues
1. **OpenAI API Key**: Ensure `config.py` has a valid API key
2. **Dependencies**: Run `pip install -r requirements.txt`
3. **Schema Files**: Ensure `input_schemas/` contains valid CSV files
4. **Input Data** (Functional Test Scenario Generation): Ensure data files are in `runs/{run_id}/input_data/`
5. **Disk Space**: Each run can generate several MB of data

### Journey-Specific Issues
- **Synthetic Data Generation**: Ensure schema files are properly formatted
- **Functional Test Scenario Generation**: Ensure input data files match schema structure
- **Business Logic Generation**: Check that run ID exists and contains data

### Logs
All agents generate detailed logs. Check the console output for:
- Directory creation messages
- API call status
- File generation progress
- Validation results

## 🤝 Contributing

To add new features or fix issues:
1. Follow the existing folder structure
2. Maintain the unique run ID system
3. Support both user journeys
4. Update this README with any changes
5. Test with both pipeline journeys

## 📄 License

This project is designed for internal use in test data generation for financial applications. 