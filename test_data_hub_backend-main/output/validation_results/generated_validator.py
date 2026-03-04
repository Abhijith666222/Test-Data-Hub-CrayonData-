import pandas as pd
import numpy as np
import json
import logging
import os
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='data_validation.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

class DataValidator:
    def __init__(self, data_files, business_rules, test_scenarios, cross_table_relationships):
        """
        data_files: dict of {table_name: path_to_csv}
        business_rules: dict of {table_name: [rules]}
        test_scenarios: dict of {table_name: [scenarios]}
        cross_table_relationships: list of relationship dicts
        """
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
        self.load_data()

    def load_data(self):
        for table, path in self.data_files.items():
            try:
                self.data[table] = pd.read_csv(path, dtype=str)
                logging.info(f"Loaded table {table} from {path} with {self.data[table].shape[0]} rows.")
            except Exception as e:
                logging.error(f"Failed to load table {table} from {path}: {e}")
                self.data[table] = pd.DataFrame()
                self.validation_results['overall_status'] = 'FAIL'
                self.validation_results['tables'][table] = {
                    'status': 'FAIL',
                    'errors': [f"Could not load data: {e}"]
                }

    def validate_all_tables(self):
        for table in self.data_files.keys():
            self.validate_table(table)
        self.validate_cross_table_relationships()

    def validate_table(self, table_name):
        if table_name not in self.data or self.data[table_name].empty:
            logging.warning(f"Skipping validation for {table_name}: No data loaded.")
            return
        table_result = {
            'business_rules': [],
            'test_scenarios': [],
            'status': 'PASS'
        }
        # Business rules
        br_results = self.validate_business_rules(table_name)
        table_result['business_rules'] = br_results
        # Test scenarios
        ts_results = self.validate_test_scenarios(table_name)
        table_result['test_scenarios'] = ts_results
        # Table status
        if any(r['status'] == 'FAIL' for r in br_results + ts_results):
            table_result['status'] = 'FAIL'
            self.validation_results['overall_status'] = 'FAIL'
        self.validation_results['tables'][table_name] = table_result

    def validate_business_rules(self, table_name):
        """
        Returns: list of dicts with keys: rule_name, status, error_count, error_samples, error_message
        """
        results = []
        df = self.data[table_name]
        rules = self.business_rules.get(table_name, [])
        for rule in rules:
            rule_name = rule['rule_name']
            error_message = rule['error_message']
            try:
                if table_name == 'customer_info':
                    if rule_name == 'Unique Customer ID':
                        dupes = df[df.duplicated('customer_id', keep=False)]
                        error_count = dupes.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = dupes['customer_id'].unique().tolist()[:5]
                    elif rule_name == 'Valid Gender':
                        invalid = df[~df['gender'].isin(['M', 'F', 'O']) | df['gender'].isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid['gender'].unique().tolist()[:5]
                    elif rule_name == 'KYC Status Consistency':
                        mismatch = df[(df['kyc_status'] == 'Verified') & (df['kyc_verified_flag'].astype(str) != '1')]
                        error_count = mismatch.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = mismatch[['customer_id', 'kyc_status', 'kyc_verified_flag']].head(5).to_dict('records')
                    elif rule_name == 'Date of Birth Validity':
                        today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
                        birth_dates = pd.to_datetime(df['birth_date'], errors='coerce')
                        invalid_birth = df[(birth_dates >= today) | birth_dates.isna()]
                        # Age check
                        age_calc = np.floor((today - birth_dates).dt.days / 365.25)
                        age_mismatch = df[(~birth_dates.isna()) & (df['age'].astype(float) != age_calc)]
                        error_count = invalid_birth.shape[0] + age_mismatch.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid_birth[['customer_id', 'birth_date']].head(3).to_dict('records') + \
                                        age_mismatch[['customer_id', 'birth_date', 'age']].head(2).to_dict('records')
                    elif rule_name == 'Annual Income Non-Negative':
                        invalid = df[df['annual_income'].astype(float) < 0]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid[['customer_id', 'annual_income']].head(5).to_dict('records')
                    else:
                        continue
                elif table_name == 'credit_card_accounts':
                    if rule_name == 'Unique Serial Number':
                        dupes = df[df.duplicated('serial_number', keep=False)]
                        error_count = dupes.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = dupes['serial_number'].unique().tolist()[:5]
                    elif rule_name == 'Valid Customer Reference':
                        customers = self.data.get('customer_info', pd.DataFrame())
                        invalid = df[~df['customer_id'].isin(customers['customer_id']) | df['customer_id'].isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid['customer_id'].unique().tolist()[:5]
                    elif rule_name == 'Credit Limit Non-Negative':
                        invalid = df[(df['credit_limit'].astype(float) < 0) | (df['max_limit'].astype(float) < 0)]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid[['serial_number', 'credit_limit', 'max_limit']].head(5).to_dict('records')
                    elif rule_name == 'Status Valid Values':
                        invalid = df[~df['status'].isin(['Active', 'Blocked', 'Closed']) | df['status'].isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid['status'].unique().tolist()[:5]
                    elif rule_name == 'Date Consistency':
                        creation = pd.to_datetime(df['creation_date'], errors='coerce')
                        closed = pd.to_datetime(df['closed_date'], errors='coerce')
                        invalid = df[(~closed.isna()) & (closed <= creation)]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid[['serial_number', 'creation_date', 'closed_date']].head(5).to_dict('records')
                    else:
                        continue
                elif table_name == 'credit_card_products':
                    if rule_name == 'Unique Product Code':
                        dupes = df[df.duplicated('product_code', keep=False)]
                        error_count = dupes.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = dupes['product_code'].unique().tolist()[:5]
                    elif rule_name == 'Active Flag Validity':
                        invalid = df[~df['active_flag'].isin(['Y', 'N']) | df['active_flag'].isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid['active_flag'].unique().tolist()[:5]
                    elif rule_name == 'Date Range Validity':
                        start = pd.to_datetime(df['start_date'], errors='coerce')
                        end = pd.to_datetime(df['end_date'], errors='coerce')
                        invalid = df[(end < start) | end.isna() | start.isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid[['product_code', 'start_date', 'end_date']].head(5).to_dict('records')
                    elif rule_name == 'Interest Rate Range':
                        invalid = df[(df['interest_rate'].astype(float) < 0) | (df['interest_rate'].astype(float) > 10)]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid[['product_code', 'interest_rate']].head(5).to_dict('records')
                    else:
                        continue
                elif table_name == 'credit_card_transactions':
                    if rule_name == 'Unique Transaction Serial Number':
                        dupes = df[df.duplicated('transaction_serial_number', keep=False)]
                        error_count = dupes.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = dupes['transaction_serial_number'].unique().tolist()[:5]
                    elif rule_name == 'Valid Account Reference':
                        accounts = self.data.get('credit_card_accounts', pd.DataFrame())
                        invalid = df[~df['serial_number'].isin(accounts['serial_number']) | df['serial_number'].isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid['serial_number'].unique().tolist()[:5]
                    elif rule_name == 'Amount Non-Negative':
                        invalid = df[(df['transaction_amount'].astype(float) < 0) | (df['final_amount'].astype(float) < 0)]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid[['transaction_serial_number', 'transaction_amount', 'final_amount']].head(5).to_dict('records')
                    elif rule_name == 'Valid Transaction Status':
                        invalid = df[~df['status'].isin(['Success', 'Declined', 'Reversed']) | df['status'].isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid['status'].unique().tolist()[:5]
                    elif rule_name == 'Date Consistency':
                        txn = pd.to_datetime(df['transaction_date'], errors='coerce')
                        post = pd.to_datetime(df['post_date'], errors='coerce')
                        invalid = df[(post < txn) | post.isna() | txn.isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid[['transaction_serial_number', 'transaction_date', 'post_date']].head(5).to_dict('records')
                    else:
                        continue
                elif table_name == 'imobile_user_session':
                    if rule_name == 'Unique Session ID':
                        dupes = df[df.duplicated('session_id', keep=False)]
                        error_count = dupes.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = dupes['session_id'].unique().tolist()[:5]
                    elif rule_name == 'Valid Customer Reference':
                        customers = self.data.get('customer_info', pd.DataFrame())
                        invalid = df[~df['customer_id'].isin(customers['customer_id']) | df['customer_id'].isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid['customer_id'].unique().tolist()[:5]
                    elif rule_name == 'Session Time Consistency':
                        start = pd.to_datetime(df['session_start_time'], errors='coerce')
                        end = pd.to_datetime(df['session_end_time'], errors='coerce')
                        invalid = df[(end <= start) | end.isna() | start.isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid[['session_id', 'session_start_time', 'session_end_time']].head(5).to_dict('records')
                    elif rule_name == 'Valid Channel':
                        invalid = df[~df['channel'].isin(['Mobile', 'Tablet', 'Web']) | df['channel'].isna()]
                        error_count = invalid.shape[0]
                        status = 'PASS' if error_count == 0 else 'FAIL'
                        error_samples = invalid['channel'].unique().tolist()[:5]
                    else:
                        continue
                else:
                    continue
                results.append({
                    'rule_name': rule_name,
                    'status': status,
                    'error_count': int(error_count),
                    'error_samples': error_samples,
                    'error_message': error_message if status == 'FAIL' else ''
                })
                if status == 'FAIL':
                    logging.warning(f"[{table_name}] Business rule '{rule_name}' failed: {error_message} (errors: {error_count})")
            except Exception as e:
                logging.error(f"Error validating business rule '{rule_name}' for table {table_name}: {e}")
                results.append({
                    'rule_name': rule_name,
                    'status': 'FAIL',
                    'error_count': -1,
                    'error_samples': [],
                    'error_message': f"Exception during validation: {e}"
                })
        return results

    def validate_test_scenarios(self, table_name):
        """
        Returns: list of dicts with keys: scenario_name, status, matched_count, error_samples, error_message
        """
        results = []
        df = self.data[table_name]
        scenarios = self.test_scenarios.get(table_name, [])
        for scenario in scenarios:
            scenario_name = scenario.get('scenario_name') or scenario.get('name')
            test_type = scenario.get('test_type', 'positive')
            try:
                # Build filter for scenario
                filter_mask = pd.Series([True] * df.shape[0])
                # For each data requirement, build mask
                reqs = scenario.get('data_requirements', {})
                for field, req in reqs.items():
                    if field not in df.columns:
                        continue
                    if req == 'Unique':
                        # Should not be duplicated
                        mask = ~df.duplicated(field, keep=False)
                    elif req == 'Duplicate value':
                        mask = df.duplicated(field, keep=False)
                    elif req == 'Non-existent':
                        # Should not exist in referenced table
                        if table_name == 'credit_card_accounts' and field == 'customer_id':
                            customers = self.data.get('customer_info', pd.DataFrame())
                            mask = ~df[field].isin(customers['customer_id'])
                        elif table_name == 'credit_card_transactions' and field == 'serial_number':
                            accounts = self.data.get('credit_card_accounts', pd.DataFrame())
                            mask = ~df[field].isin(accounts['serial_number'])
                        elif table_name == 'imobile_user_session' and field == 'customer_id':
                            customers = self.data.get('customer_info', pd.DataFrame())
                            mask = ~df[field].isin(customers['customer_id'])
                        else:
                            mask = pd.Series([False] * df.shape[0])
                    elif req == 'Exists in customer_info':
                        customers = self.data.get('customer_info', pd.DataFrame())
                        mask = df[field].isin(customers['customer_id'])
                    elif req == 'Exists in credit_card_accounts':
                        accounts = self.data.get('credit_card_accounts', pd.DataFrame())
                        mask = df[field].isin(accounts['serial_number'])
                    elif req == 'Active':
                        mask = df[field] == 'Active'
                    elif req == 'Blocked':
                        mask = df[field] == 'Blocked'
                    elif req == 'Closed':
                        mask = df[field] == 'Closed'
                    elif req == 'Y':
                        mask = df[field] == 'Y'
                    elif req == 'N':
                        mask = df[field] == 'N'
                    elif req == 'true':
                        mask = df[field].astype(str).str.lower() == 'true'
                    elif req == 'false':
                        mask = df[field].astype(str).str.lower() == 'false'
                    elif req == 'Non-empty':
                        mask = df[field].notna() & (df[field].astype(str).str.strip() != '')
                    elif req == 'Invalid value':
                        # For negative scenario, value not in allowed set
                        if field == 'gender':
                            mask = ~df[field].isin(['M', 'F', 'O'])
                        elif field == 'active_flag':
                            mask = ~df[field].isin(['Y', 'N'])
                        elif field == 'channel':
                            mask = ~df[field].isin(['Mobile', 'Tablet', 'Web'])
                        else:
                            mask = pd.Series([False] * df.shape[0])
                    elif req == '>= 0':
                        mask = df[field].astype(float) >= 0
                    elif req == '< 0':
                        mask = df[field].astype(float) < 0
                    elif req == '0':
                        mask = df[field].astype(float) == 0
                    else:
                        # Try to match sample value
                        mask = df[field].astype(str) == str(req)
                    filter_mask &= mask
                matched = df[filter_mask]
                matched_count = matched.shape[0]
                # For negative scenarios, expect failures
                if test_type == 'negative':
                    status = 'PASS' if matched_count > 0 else 'FAIL'
                else:
                    status = 'PASS' if matched_count > 0 else 'FAIL'
                error_samples = matched.head(5).to_dict('records')
                error_message = '' if status == 'PASS' else f"No records matched scenario: {scenario_name}"
                results.append({
                    'scenario_name': scenario_name,
                    'status': status,
                    'matched_count': int(matched_count),
                    'error_samples': error_samples,
                    'error_message': error_message
                })
                if status == 'FAIL':
                    logging.warning(f"[{table_name}] Test scenario '{scenario_name}' failed: {error_message}")
            except Exception as e:
                logging.error(f"Error validating test scenario '{scenario_name}' for table {table_name}: {e}")
                results.append({
                    'scenario_name': scenario_name,
                    'status': 'FAIL',
                    'matched_count': -1,
                    'error_samples': [],
                    'error_message': f"Exception during validation: {e}"
                })
        return results

    def validate_cross_table_relationships(self):
        """
        Validates all cross-table relationships and appends results to self.validation_results['cross_table']
        """
        for rel in self.cross_table_relationships:
            from_table = rel['from_table']
            to_table = rel['to_table']
            fk = rel['foreign_key']
            rel_type = rel['relationship_type']
            try:
                df_from = self.data.get(from_table, pd.DataFrame())
                df_to = self.data.get(to_table, pd.DataFrame())
                if df_from.empty or df_to.empty:
                    status = 'FAIL'
                    error_message = f"Missing data for {from_table} or {to_table}"
                    error_count = -1
                    error_samples = []
                else:
                    invalid = df_from[~df_from[fk].isin(df_to[df_to.columns[0]]) | df_from[fk].isna()]
                    error_count = invalid.shape[0]
                    status = 'PASS' if error_count == 0 else 'FAIL'
                    error_samples = invalid[[fk]].head(5).to_dict('records')
                    error_message = '' if status == 'PASS' else f"{error_count} records in {from_table}.{fk} do not reference valid {to_table}.{df_to.columns[0]}"
                self.validation_results['cross_table'].append({
                    'from_table': from_table,
                    'to_table': to_table,
                    'foreign_key': fk,
                    'status': status,
                    'error_count': int(error_count),
                    'error_samples': error_samples,
                    'error_message': error_message
                })
                if status == 'FAIL':
                    self.validation_results['overall_status'] = 'FAIL'
                    logging.warning(f"Cross-table validation failed: {error_message}")
            except Exception as e:
                logging.error(f"Error in cross-table validation {from_table}->{to_table} ({fk}): {e}")
                self.validation_results['cross_table'].append({
                    'from_table': from_table,
                    'to_table': to_table,
                    'foreign_key': fk,
                    'status': 'FAIL',
                    'error_count': -1,
                    'error_samples': [],
                    'error_message': f"Exception during validation: {e}"
                })
                self.validation_results['overall_status'] = 'FAIL'

    def generate_validation_report(self):
        # Data quality metrics
        summary = {}
        for table, df in self.data.items():
            if df.empty:
                summary[table] = {'row_count': 0, 'missing_values': {}}
                continue
            missing = df.isna().sum().to_dict()
            summary[table] = {
                'row_count': df.shape[0],
                'missing_values': {k: int(v) for k, v in missing.items() if v > 0}
            }
        self.validation_results['summary'] = summary

    def save_validation_results(self, output_path):
        # Save JSON report
        json_path = os.path.join(output_path, 'validation_report.json')
        with open(json_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2, default=str)
        # Save human-readable summary
        txt_path = os.path.join(output_path, 'validation_summary.txt')
        with open(txt_path, 'w') as f:
            f.write(f"Overall Validation Status: {self.validation_results['overall_status']}\n\n")
            for table, result in self.validation_results['tables'].items():
                f.write(f"Table: {table}\n")
                f.write(f"  Status: {result['status']}\n")
                f.write("  Business Rules:\n")
                for br in result['business_rules']:
                    f.write(f"    - {br['rule_name']}: {br['status']} (Errors: {br['error_count']})\n")
                    if br['status'] == 'FAIL':
                        f.write(f"      Error Message: {br['error_message']}\n")
                        f.write(f"      Samples: {br['error_samples']}\n")
                f.write("  Test Scenarios:\n")
                for ts in result['test_scenarios']:
                    f.write(f"    - {ts['scenario_name']}: {ts['status']} (Matched: {ts['matched_count']})\n")
                    if ts['status'] == 'FAIL':
                        f.write(f"      Error Message: {ts['error_message']}\n")
                        f.write(f"      Samples: {ts['error_samples']}\n")
                f.write("\n")
            f.write("Cross-table Relationship Validations:\n")
            for rel in self.validation_results['cross_table']:
                f.write(f"  {rel['from_table']}->{rel['to_table']} ({rel['foreign_key']}): {rel['status']} (Errors: {rel['error_count']})\n")
                if rel['status'] == 'FAIL':
                    f.write(f"    Error Message: {rel['error_message']}\n")
                    f.write(f"    Samples: {rel['error_samples']}\n")
            f.write("\nData Quality Metrics:\n")
            for table, summ in self.validation_results['summary'].items():
                f.write(f"  {table}: {summ['row_count']} rows\n")
                if summ['missing_values']:
                    f.write(f"    Missing values: {summ['missing_values']}\n")
            f.write("\n")

# Example usage
if __name__ == '__main__':
    # Paths to CSVs (replace with your actual file paths)
    data_files = {
        'customer_info': 'customer_info.csv',
        'credit_card_accounts': 'credit_card_accounts.csv',
        'credit_card_products': 'credit_card_products.csv',
        'credit_card_transactions': 'credit_card_transactions.csv',
        'imobile_user_session': 'imobile_user_session.csv'
    }

    # Load business rules, test scenarios, cross-table relationships from JSON or define here
    # For this example, assume they're loaded from files or variables as per your analysis results
    # Replace the following with actual data as per your environment
    with open('business_rules.json') as f:
        business_rules = json.load(f)
    with open('test_scenarios.json') as f:
        test_scenarios = json.load(f)
    with open('cross_table_relationships.json') as f:
        cross_table_relationships = json.load(f)

    # Output directory
    output_path = '.'

    # Run validation
    validator = DataValidator(
        data_files=data_files,
        business_rules=business_rules,
        test_scenarios=test_scenarios,
        cross_table_relationships=cross_table_relationships
    )
    validator.validate_all_tables()
    validator.generate_validation_report()
    validator.save_validation_results(output_path)
    print("Validation complete. See validation_report.json and validation_summary.txt for details.")