# Business Logic Library

This directory contains a comprehensive library of business rules and test scenarios for the credit card system, along with a chat agent to generate new ones from natural language prompts.

## Files

- `business_rules.csv` - Contains business rules for data validation
- `test_scenarios.csv` - Contains test scenarios for comprehensive testing
- `library_generator_agent.py` - Chat agent to generate new business logic from natural language

## Usage

### 1. View Current Library

To see what's currently in the library:

```bash
python business_logic_library/library_generator_agent.py
# Then type 'summary' when prompted for table name
```

### 2. Generate New Business Logic

Run the chat agent:

```bash
python business_logic_library/library_generator_agent.py
```

The agent will automatically:
1. **Analyze your description** - Detect which tables are affected by your business logic
2. **Generate business rules and test scenarios** - Create appropriate validation rules and test cases
3. **Show you the results** - Display what was generated for each table
4. **Ask for confirmation** - Let you approve before adding to the library

Just describe your business logic in natural language - no need to specify table names!

### 3. Example Prompts

Here are some example prompts you can use:

#### For credit_card_accounts:
- "Accounts should not allow transactions if the card is expired"
- "Credit limit should be based on customer's annual income"
- "Blocked accounts should have a reason recorded"

#### For credit_card_transactions:
- "High-value transactions should trigger additional verification"
- "International transactions should have foreign transaction fees"
- "Declined transactions should not earn reward points"

#### For imobile_user_session:
- "Sessions from new devices should require additional verification"
- "Failed login attempts should be tracked and limited"
- "Biometric authentication should only work for verified customers"

#### For customer_info:
- "Minors should not be able to open credit card accounts"
- "KYC verification should be required for high-value customers"
- "Customers with poor payment history should have restricted access"

#### For credit_card_products:
- "Interest rates should be within regulatory limits"
- "Annual fees should be waived for premium customers"
- "Product end dates should be after start dates"

### 4. CSV Structure

#### Business Rules CSV Columns:
- `table_name` - Target table
- `rule_name` - Descriptive name
- `rule_type` - uniqueness, referential, range, enumeration, business_logic
- `description` - Clear description
- `validation_logic` - SQL-like validation logic
- `error_message` - Error message when violated
- `severity` - CRITICAL, HIGH, MEDIUM, LOW
- `is_active` - 1 for active rules

#### Test Scenarios CSV Columns:
- `table_name` - Target table
- `scenario_name` - Descriptive name
- `scenario_type` - positive, negative, edge_case
- `description` - Clear description
- `test_conditions` - Conditions to test
- `expected_behavior` - Expected outcome
- `data_requirements` - Specific data needs
- `priority` - HIGH, MEDIUM, LOW, CRITICAL
- `is_active` - 1 for active scenarios

## Features

### Cross-Table Relationships
The library includes scenarios that test relationships between tables:
- Customer sessions with active/blocked accounts
- Transactions for customers with specific account statuses
- Account creation based on customer KYC status
- Mobile banking access based on account status

### Comprehensive Coverage
- **Positive scenarios** - Normal, expected behavior
- **Negative scenarios** - Error conditions and edge cases
- **Business logic validation** - Complex rules involving multiple tables
- **Security scenarios** - Fraud detection and prevention
- **Compliance scenarios** - Regulatory requirements

### Easy Extension
The chat agent makes it easy to add new business logic:
1. Describe your requirement in natural language
2. The AI generates appropriate business rules and test scenarios
3. Review and confirm before adding to the library
4. The library automatically grows with your needs

## Integration

This library can be used with:
- **Schema Analysis Agent** - To understand existing business rules
- **Synthetic Data Generator** - To generate data that follows these rules
- **Validation Agent** - To validate data against these rules and scenarios

## Tips for Good Prompts

1. **Be specific** - "High-value transactions over $10,000" vs "large transactions"
2. **Mention relationships** - "Customers with blocked accounts" vs "blocked accounts"
3. **Include conditions** - "When KYC is pending" vs "KYC requirements"
4. **Specify outcomes** - "Should be declined" vs "should be handled"
5. **Consider edge cases** - "What if the customer has multiple accounts?"

## Example Session

```
Describe the business logic or test scenario: Transactions for customers with blocked accounts should be declined automatically

Analyzing your requirement...
📋 Detected relevant tables: credit_card_accounts, credit_card_transactions

🔧 Generating business logic for credit_card_accounts...
🔧 Generating business logic for credit_card_transactions...

🎯 Generated 2 business rules and 4 test scenarios:

📋 BUSINESS RULES:
  1. [credit_card_accounts] Blocked Account Status Validation: Blocked accounts should have valid status
  2. [credit_card_transactions] Blocked Account Transaction Validation: Transactions for customers with blocked accounts should be declined

🧪 TEST SCENARIOS:
  1. [credit_card_accounts] Account with Blocked Status: Account should be properly flagged as blocked
  2. [credit_card_accounts] Account with Active Status: Account should allow normal operations
  3. [credit_card_transactions] Transaction for Customer with Blocked Account: Transaction should be declined when account is blocked
  4. [credit_card_transactions] Transaction for Customer with Active Account: Transaction should proceed when account is active

✅ Add these to the library? (y/n): y
🎉 Successfully added to library!
``` 