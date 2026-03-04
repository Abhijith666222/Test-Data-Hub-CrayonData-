import os
import pandas as pd
import numpy as np
import random
import uuid
import time
from datetime import datetime, timedelta
from faker import Faker
from collections import defaultdict, Counter

class SyntheticDataGenerator:
    def __init__(self, config):
        self.config = config
        self.seed = config.get('seed', 42)
        random.seed(self.seed)
        np.random.seed(self.seed)
        self.faker = Faker()
        Faker.seed(self.seed)
        self.generation_order = [
            'customer_info',
            'credit_card_products',
            'credit_card_accounts',
            'credit_card_transactions',
            'imobile_user_session'
        ]
        self.volume_overrides = config.get('volume_overrides', {})
        self.scenario_mix = config.get('scenario_mix', {'positive': 0.7, 'negative': 0.2, 'edge_case': 0.1})
        self.data_distribution = self._get_data_distribution()
        self.generated_data = {}
        self.unique_sets = defaultdict(set)
        self.test_scenarios = self._get_test_scenarios()
        self.business_rules = self._get_business_rules()
        self.output_format = config.get('output_format', 'csv')
        self.output_dir = config.get('output_dir', '.')
        self._precompute_reference_lists()

    def _get_data_distribution(self):
        # Hardcoded from requirements
        return {
            ('customer_info', 'annual_income'): {
                'type': 'log-normal',
                'mean': 13,
                'stddev': 0.7
            },
            ('customer_info', 'gender'): {
                'type': 'categorical',
                'parameters': {'M': 0.49, 'F': 0.49, 'O': 0.02}
            },
            ('credit_card_accounts', 'status'): {
                'type': 'categorical',
                'parameters': {'Active': 0.85, 'Blocked': 0.05, 'Closed': 0.1}
            },
            ('credit_card_products', 'active_flag'): {
                'type': 'categorical',
                'parameters': {'Y': 0.8, 'N': 0.2}
            },
            ('credit_card_products', 'interest_rate'): {
                'type': 'uniform',
                'min': 1.5,
                'max': 3.5
            },
            ('credit_card_transactions', 'status'): {
                'type': 'categorical',
                'parameters': {'Success': 0.92, 'Declined': 0.06, 'Reversed': 0.02}
            },
            ('credit_card_transactions', 'transaction_amount'): {
                'type': 'exponential',
                'lambda': 0.0001
            },
            ('imobile_user_session', 'channel'): {
                'type': 'categorical',
                'parameters': {'Mobile': 0.85, 'Tablet': 0.1, 'Web': 0.05}
            }
        }

    def _get_test_scenarios(self):
        # Hardcoded from requirements for each table
        return {
            'customer_info': [
                {
                    'type': 'positive',
                    'fields': {
                        'customer_id': 'RIM00012345',
                        'gender': 'M',
                        'kyc_status': 'Verified',
                        'kyc_verified_flag': 1,
                        'annual_income': 1000000
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'customer_id': 'RIM00012345'  # Duplicate
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'gender': 'X'
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'kyc_status': 'Verified',
                        'kyc_verified_flag': 0
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'annual_income': -50000
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'birth_date': '2099-01-01'
                    }
                }
            ],
            'credit_card_products': [
                {
                    'type': 'positive',
                    'fields': {
                        'product_code': 'VISA123',
                        'active_flag': 'Y',
                        'interest_rate': 2.99
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'product_code': 'VISA123'  # Duplicate
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'active_flag': 'A'
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'start_date': '2025-01-01',
                        'end_date': '2024-12-31'
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'interest_rate': 15.00
                    }
                }
            ],
            'credit_card_accounts': [
                {
                    'type': 'positive',
                    'fields': {
                        'customer_id': 'RIM00012345',
                        'status': 'Active',
                        'credit_limit': 150000,
                        'serial_number': 'P123456'
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'serial_number': 'P123456'  # Duplicate
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'credit_limit': -1000
                    }
                },
                {
                    'type': 'positive',
                    'fields': {
                        'creation_date': '2021-03-15',
                        'closed_date': '2023-12-30'
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'customer_id': 'RIM99999999'
                    }
                },
                {
                    'type': 'positive',
                    'fields': {
                        'status': 'Blocked',
                        'block_reason': 'Fraud suspected'
                    }
                }
            ],
            'credit_card_transactions': [
                {
                    'type': 'positive',
                    'fields': {
                        'serial_number': 'P123456',
                        'status': 'Success',
                        'transaction_amount': 2500
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'serial_number': 'P999999'
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'transaction_amount': -100
                    }
                },
                {
                    'type': 'positive',
                    'fields': {
                        'status': 'Declined',
                        'points_earned': 0
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'transaction_date': '2025-08-01',
                        'post_date': '2025-07-31'
                    }
                },
                {
                    'type': 'positive',
                    'fields': {
                        'is_online': True,
                        'local_international': 'I'
                    }
                }
            ],
            'imobile_user_session': [
                {
                    'type': 'positive',
                    'fields': {
                        'session_id': 'sess_ABC123',
                        'customer_id': 'RIM00012345',
                        'channel': 'Mobile',
                        'session_start_time': '2025-08-01 09:00',
                        'session_end_time': '2025-08-01 09:30'
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'customer_id': 'RIM99999999'
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'session_start_time': '2025-08-01 10:00',
                        'session_end_time': '2025-08-01 09:00'
                    }
                },
                {
                    'type': 'negative',
                    'fields': {
                        'channel': 'Desktop'
                    }
                },
                {
                    'type': 'positive',
                    'fields': {
                        'first_login': 'Y',
                        'biometric_enabled': 'Y'
                    }
                }
            ]
        }

    def _get_business_rules(self):
        # Hardcoded from requirements for each table
        return {
            'customer_info': [
                self._rule_unique_customer_id,
                self._rule_valid_gender,
                self._rule_kyc_status_consistency,
                self._rule_birth_date_validity,
                self._rule_annual_income_non_negative
            ],
            'credit_card_products': [
                self._rule_unique_product_code,
                self._rule_active_flag_validity,
                self._rule_product_date_range_validity,
                self._rule_interest_rate_range
            ],
            'credit_card_accounts': [
                self._rule_unique_serial_number,
                self._rule_valid_customer_reference,
                self._rule_credit_limit_non_negative,
                self._rule_status_valid_values,
                self._rule_account_date_consistency
            ],
            'credit_card_transactions': [
                self._rule_unique_transaction_serial_number,
                self._rule_valid_account_reference,
                self._rule_transaction_amount_non_negative,
                self._rule_transaction_status_valid,
                self._rule_transaction_date_consistency
            ],
            'imobile_user_session': [
                self._rule_unique_session_id,
                self._rule_valid_customer_reference_session,
                self._rule_session_time_consistency,
                self._rule_valid_channel
            ]
        }

    def _precompute_reference_lists(self):
        # For referential integrity, precompute empty lists to be filled after generation
        self.reference_lists = {
            'customer_info': [],
            'credit_card_products': [],
            'credit_card_accounts': []
        }

    def generate_all_data(self):
        for table in self.generation_order:
            print(f"Generating data for table: {table}")
            self.generated_data[table] = self.generate_table_data(table)
            # Update reference lists for referential integrity
            if table == 'customer_info':
                self.reference_lists['customer_info'] = self.generated_data[table]['customer_id'].tolist()
            elif table == 'credit_card_products':
                self.reference_lists['credit_card_products'] = self.generated_data[table]['product_code'].tolist()
            elif table == 'credit_card_accounts':
                self.reference_lists['credit_card_accounts'] = self.generated_data[table]['serial_number'].tolist()

    def generate_table_data(self, table_name):
        volume = self.volume_overrides.get(table_name, 100)
        scenario_counts = self._get_scenario_counts(volume, table_name)
        data = []
        # 1. Inject test scenarios
        data += self.inject_test_scenarios([], table_name, scenario_counts)
        # 2. Generate the rest of the data
        remaining = volume - len(data)
        for _ in range(remaining):
            row = self._generate_row(table_name)
            data.append(row)
        # 3. Convert to DataFrame
        df = pd.DataFrame(data)
        # 4. Apply business rules
        df = self.apply_business_rules(df, table_name)
        # 5. Fill missing columns with NaN
        df = self._ensure_all_columns(df, table_name)
        return df

    def _get_scenario_counts(self, volume, table_name):
        # Calculate number of positive, negative, edge_case rows to inject
        scenarios = self.test_scenarios.get(table_name, [])
        type_counts = Counter([s['type'] for s in scenarios])
        total_types = {k: v for k, v in type_counts.items() if v > 0}
        mix = self.scenario_mix
        counts = {}
        for t in ['positive', 'negative', 'edge_case']:
            n = int(volume * mix.get(t, 0))
            # Don't inject more than available scenarios of that type
            available = sum(1 for s in scenarios if s['type'] == t)
            counts[t] = min(n, available)
        return counts

    def inject_test_scenarios(self, data, table_name, scenario_counts):
        scenarios = self.test_scenarios.get(table_name, [])
        used = set()
        injected = []
        for t in ['positive', 'negative', 'edge_case']:
            count = scenario_counts.get(t, 0)
            candidates = [s for i, s in enumerate(scenarios) if s['type'] == t and i not in used]
            for i in range(min(count, len(candidates))):
                scenario = candidates[i]
                row = self._generate_row(table_name, override_fields=scenario['fields'])
                injected.append(row)
                used.add(i)
        return injected

    def apply_business_rules(self, df, table_name):
        rules = self.business_rules.get(table_name, [])
        for rule in rules:
            df = rule(df)
        return df

    def save_to_csv(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for table, df in self.generated_data.items():
            filename = os.path.join(output_dir, f"{table}.csv")
            df.to_csv(filename, index=False)

    # ----------------- Row Generation Functions -----------------

    def _generate_row(self, table_name, override_fields=None):
        override_fields = override_fields or {}
        if table_name == 'customer_info':
            return self._generate_customer_info_row(override_fields)
        elif table_name == 'credit_card_products':
            return self._generate_credit_card_products_row(override_fields)
        elif table_name == 'credit_card_accounts':
            return self._generate_credit_card_accounts_row(override_fields)
        elif table_name == 'credit_card_transactions':
            return self._generate_credit_card_transactions_row(override_fields)
        elif table_name == 'imobile_user_session':
            return self._generate_imobile_user_session_row(override_fields)
        else:
            return {}

    def _generate_customer_info_row(self, override_fields):
        # Unique customer_id
        customer_id = override_fields.get('customer_id')
        if not customer_id:
            while True:
                candidate = f"RIM{str(random.randint(10000000, 99999999))}"
                if candidate not in self.unique_sets['customer_id']:
                    customer_id = candidate
                    self.unique_sets['customer_id'].add(candidate)
                    break
        else:
            if customer_id not in self.unique_sets['customer_id']:
                self.unique_sets['customer_id'].add(customer_id)
        # Gender
        gender = override_fields.get('gender')
        if not gender:
            gender = self._random_categorical({'M': 0.49, 'F': 0.49, 'O': 0.02})
        # KYC
        kyc_status = override_fields.get('kyc_status', random.choice(['Verified', 'In progress', None]))
        if kyc_status == 'Verified':
            kyc_verified_flag = override_fields.get('kyc_verified_flag', 1)
        else:
            kyc_verified_flag = override_fields.get('kyc_verified_flag', random.choice([0, 1]))
        # Annual income
        annual_income = override_fields.get('annual_income')
        if annual_income is None:
            dist = self.data_distribution.get(('customer_info', 'annual_income'))
            if dist and dist['type'] == 'log-normal':
                val = np.random.lognormal(mean=dist['mean'], sigma=dist['stddev'])
                annual_income = float(np.clip(val, 100000, 10000000))
            else:
                annual_income = float(random.randint(100000, 10000000))
        # Date of birth and age
        birth_date = override_fields.get('birth_date')
        if not birth_date:
            try:
                today = datetime.now()
                min_age = 18
                max_age = 75
                age = random.randint(min_age, max_age)
                birth_date_dt = today - timedelta(days=age * 365 + random.randint(0, 364))
                birth_date = birth_date_dt.strftime('%Y-%m-%d')
            except Exception:
                birth_date = '1980-01-01'
        else:
            # If override is string, keep as is
            pass
        # Age
        try:
            age = int((datetime.now() - datetime.strptime(str(birth_date), '%Y-%m-%d')).days // 365.25)
        except Exception:
            age = 30
        # Age group
        if age < 26:
            age_group = '18-25'
        elif age < 36:
            age_group = '26-35'
        elif age < 51:
            age_group = '36-50'
        else:
            age_group = '51+'
        # Other fields
        record_type = override_fields.get('record_type', 'I')
        class_code = override_fields.get('class_code', random.choice(['001', '101', '201']))
        city_of_birth = override_fields.get('city_of_birth', self.faker.city())
        country_code = override_fields.get('country_code', random.choice(['IN', 'AE']))
        language = override_fields.get('language', random.choice(['EN', 'HI']))
        nationality = override_fields.get('nationality', 'Indian' if country_code == 'IN' else 'Emirati')
        profession = override_fields.get('profession', random.choice(['Engineer', 'Teacher', 'Retired', 'Doctor', 'Banker']))
        marital_status = override_fields.get('marital_status', random.choice(['Single', 'Married', 'Divorced']))
        city = override_fields.get('city', self.faker.city())
        address = override_fields.get('address', self.faker.address().replace('\n', ', '))
        # Created/closed dates
        try:
            created_date = (datetime.now() - timedelta(days=random.randint(1, 365*5))).strftime('%Y-%m-%d')
        except Exception:
            created_date = '2020-01-01'
        closed_date = override_fields.get('closed_date')
        if not closed_date and random.random() < 0.05:
            try:
                closed_date_dt = datetime.strptime(created_date, '%Y-%m-%d') + timedelta(days=random.randint(30, 365*3))
                if closed_date_dt > datetime.now():
                    closed_date = None
                else:
                    closed_date = closed_date_dt.strftime('%Y-%m-%d')
            except Exception:
                closed_date = None
        status = override_fields.get('status', random.choice(['Active', 'Closed', 'Dormant']))
        employer_id = override_fields.get('employer_id', f"EMP{random.randint(10000,99999)}")
        employer_name = override_fields.get('employer_name', random.choice(['Infosys', 'TCS', 'HDFC', 'ICICI', 'Reliance']))
        employer_sector = override_fields.get('employer_sector', random.choice(['IT', 'Banking', 'Government', 'Private']))
        employer_name_clean = employer_name.upper() + " LTD"
        employer_name_redundant = employer_name_clean
        class_code_desc = override_fields.get('class_code_desc', random.choice(['High Net Worth', 'Retail Customer']))
        business_unit = override_fields.get('business_unit', random.choice(['BU101', 'North Zone', 'South Zone']))
        segment = override_fields.get('segment', random.choice(['Retail', 'Premium', 'SME']))
        kyc_id_type = override_fields.get('kyc_id_type', random.choice(['Aadhar', 'Passport', 'Emirates ID']))
        kyc_id_number = override_fields.get('kyc_id_number', self.faker.bothify(text='####-XXXX-######-#'))
        kyc_id_expiry = override_fields.get('kyc_id_expiry')
        if not kyc_id_expiry:
            try:
                kyc_id_expiry_dt = datetime.now() + timedelta(days=random.randint(365, 365*10))
                kyc_id_expiry = kyc_id_expiry_dt.strftime('%Y-%m-%d')
            except Exception:
                kyc_id_expiry = '2030-12-31'
        kyc_last_verified = override_fields.get('kyc_last_verified')
        if not kyc_last_verified:
            try:
                kyc_last_verified_dt = datetime.now() - timedelta(days=random.randint(1, 365*2))
                kyc_last_verified = kyc_last_verified_dt.strftime('%Y-%m-%d')
            except Exception:
                kyc_last_verified = '2023-01-15'
        kyc_status = kyc_status
        kyc_verified_flag = kyc_verified_flag
        imobile_registered = override_fields.get('imobile_registered', random.choice(['Y', 'N']))
        # Compose row
        row = {
            'customer_id': customer_id,
            'record_type': record_type,
            'class_code': class_code,
            'birth_date': birth_date,
            'city_of_birth': city_of_birth,
            'country_code': country_code,
            'gender': gender,
            'language': language,
            'nationality': nationality,
            'profession': profession,
            'age': age,
            'age_group': age_group,
            'marital_status': marital_status,
            'city': city,
            'address': address,
            'created_date': created_date,
            'closed_date': closed_date,
            'status': status,
            'employer_id': employer_id,
            'employer_name': employer_name,
            'employer_sector': employer_sector,
            'employer_name_clean': employer_name_clean,
            'employer_name_redundant': employer_name_redundant,
            'class_code_desc': class_code_desc,
            'business_unit': business_unit,
            'segment': segment,
            'kyc_id_type': kyc_id_type,
            'kyc_id_number': kyc_id_number,
            'kyc_id_expiry': kyc_id_expiry,
            'kyc_last_verified': kyc_last_verified,
            'kyc_status': kyc_status,
            'kyc_verified_flag': kyc_verified_flag,
            'imobile_registered': imobile_registered,
            'annual_income': annual_income
        }
        # Apply overrides
        for k, v in override_fields.items():
            row[k] = v
        return row

    def _generate_credit_card_products_row(self, override_fields):
        # Unique product_code
        product_code = override_fields.get('product_code')
        if not product_code:
            while True:
                candidate = random.choice(['VISA', 'PLATINUM', 'GOLD', 'AMEX', 'MASTERCARD']) + str(random.randint(100,999))
                if candidate not in self.unique_sets['product_code']:
                    product_code = candidate
                    self.unique_sets['product_code'].add(candidate)
                    break
        else:
            if product_code not in self.unique_sets['product_code']:
                self.unique_sets['product_code'].add(product_code)
        # Name
        product_name = override_fields.get('product_name', random.choice([
            'Platinum Credit Card', 'Gold Credit Card', 'Titanium Card', 'Cashback Card', 'Travel Card'
        ]))
        card_type = override_fields.get('card_type', random.choice(['VISA', 'MASTERCARD', 'AMEX']))
        secured = override_fields.get('secured', random.choice(['Secured', 'Unsecured']))
        segmentation = override_fields.get('segmentation', random.choice(['Gold', 'Platinum', 'Titanium']))
        currency = override_fields.get('currency', random.choice(['INR', 'AED', 'USD']))
        channel = override_fields.get('channel', random.choice(['Branch', 'Online', 'Mobile']))
        bank = override_fields.get('bank', random.choice(['Bank XYZ', 'ABC Bank', 'ICICI', 'HDFC']))
        # Dates
        try:
            start_date_dt = datetime.now() - timedelta(days=random.randint(1, 365*5))
            start_date = override_fields.get('start_date', start_date_dt.strftime('%Y-%m-%d'))
            end_date_dt = start_date_dt + timedelta(days=random.randint(365, 365*10))
            end_date = override_fields.get('end_date', end_date_dt.strftime('%Y-%m-%d'))
        except Exception:
            start_date = '2021-01-01'
            end_date = '2099-12-31'
        reward_program = override_fields.get('reward_program', random.choice(['Miles', 'Cashback', 'None']))
        default_credit_limit = override_fields.get('default_credit_limit', float(random.randint(50000, 200000)))
        annual_fee = override_fields.get('annual_fee', float(random.randint(500, 1500)))
        # Interest rate
        interest_rate = override_fields.get('interest_rate')
        if interest_rate is None:
            dist = self.data_distribution.get(('credit_card_products', 'interest_rate'))
            if dist and dist['type'] == 'uniform':
                interest_rate = round(random.uniform(dist['min'], dist['max']), 2)
            else:
                interest_rate = round(random.uniform(1.5, 3.5), 2)
        billing_cycle_days = override_fields.get('billing_cycle_days', random.choice([30, 45]))
        created_date = override_fields.get('created_date', (datetime.now() - timedelta(days=random.randint(1, 365*2))).strftime('%Y-%m-%d'))
        last_updated = override_fields.get('last_updated', (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d %H:%M'))
        # Active flag
        active_flag = override_fields.get('active_flag')
        if not active_flag:
            active_flag = self._random_categorical({'Y': 0.8, 'N': 0.2})
        row = {
            'product_code': product_code,
            'product_name': product_name,
            'card_type': card_type,
            'secured': secured,
            'segmentation': segmentation,
            'currency': currency,
            'channel': channel,
            'bank': bank,
            'start_date': start_date,
            'end_date': end_date,
            'reward_program': reward_program,
            'default_credit_limit': default_credit_limit,
            'annual_fee': annual_fee,
            'interest_rate': interest_rate,
            'billing_cycle_days': billing_cycle_days,
            'created_date': created_date,
            'last_updated': last_updated,
            'active_flag': active_flag
        }
        for k, v in override_fields.items():
            row[k] = v
        return row

    def _generate_credit_card_accounts_row(self, override_fields):
        # serial_number
        serial_number = override_fields.get('serial_number')
        if not serial_number:
            while True:
                candidate = f"P{random.randint(100000,999999)}"
                if candidate not in self.unique_sets['serial_number']:
                    serial_number = candidate
                    self.unique_sets['serial_number'].add(candidate)
                    break
        else:
            if serial_number not in self.unique_sets['serial_number']:
                self.unique_sets['serial_number'].add(serial_number)
        # customer_id
        customer_id = override_fields.get('customer_id')
        if not customer_id:
            if self.reference_lists['customer_info']:
                customer_id = random.choice(self.reference_lists['customer_info'])
            else:
                customer_id = f"RIM{random.randint(10000000,99999999)}"
        # credit_card_number (masked)
        credit_card_number = override_fields.get('credit_card_number')
        if not credit_card_number:
            cc_num = self._generate_luhn_card_number()
            credit_card_number = f"{cc_num[:4]}-XXXX-XXXX-{cc_num[-4:]}"
        # Card type
        card_type = override_fields.get('card_type', random.choice(['VISA', 'MASTERCARD', 'AMEX']))
        # Status
        status = override_fields.get('status')
        if not status:
            dist = self.data_distribution.get(('credit_card_accounts', 'status'))
            if dist and dist['type'] == 'categorical':
                status = self._random_categorical(dist['parameters'])
            else:
                status = random.choice(['Active', 'Blocked', 'Closed'])
        # Billing method
        billing_method = override_fields.get('billing_method', random.choice(['Cycle', 'Manual']))
        # Product code
        product_code = override_fields.get('product_code')
        if not product_code:
            if self.reference_lists['credit_card_products']:
                product_code = random.choice(self.reference_lists['credit_card_products'])
            else:
                product_code = 'VISA123'
        # Card currency
        card_currency = override_fields.get('card_currency', random.choice(['INR', 'AED']))
        # Credit limit
        credit_limit = override_fields.get('credit_limit', float(random.randint(50000, 200000)))
        max_limit = override_fields.get('max_limit', credit_limit + random.randint(0, 50000))
        # Outstanding balance
        outstanding_balance = override_fields.get('outstanding_balance', round(random.uniform(0, credit_limit), 2))
        reward_points = override_fields.get('reward_points', random.randint(0, 5000))
        reward_point_txns = override_fields.get('reward_point_txns', random.randint(0, 100))
        amount_overdue = override_fields.get('amount_overdue', round(random.uniform(0, 5000), 2))
        overdue_since = override_fields.get('overdue_since')
        if not overdue_since and amount_overdue > 0:
            try:
                overdue_since_dt = datetime.now() - timedelta(days=random.randint(1, 60))
                overdue_since = overdue_since_dt.strftime('%Y-%m-%d')
            except Exception:
                overdue_since = None
        due_date = override_fields.get('due_date')
        if not due_date:
            try:
                due_date_dt = datetime.now() + timedelta(days=random.randint(1, 30))
                due_date = due_date_dt.strftime('%Y-%m-%d')
            except Exception:
                due_date = None
        min_amount_due = override_fields.get('min_amount_due', round(random.uniform(1000, 5000), 2))
        total_credited = override_fields.get('total_credited', round(random.uniform(0, credit_limit), 2))
        total_debited = override_fields.get('total_debited', round(random.uniform(0, credit_limit), 2))
        last_billing_date = override_fields.get('last_billing_date')
        if not last_billing_date:
            try:
                last_billing_date_dt = datetime.now() - timedelta(days=random.randint(1, 30))
                last_billing_date = last_billing_date_dt.strftime('%Y-%m-%d')
            except Exception:
                last_billing_date = None
        last_payment_ref = override_fields.get('last_payment_ref', f"PAY{random.randint(1000000,9999999)}")
        partition_key = override_fields.get('partition_key', datetime.now().strftime('%Y%m'))
        active_emi_plans = override_fields.get('active_emi_plans', random.randint(0, 5))
        emi_outstanding = override_fields.get('emi_outstanding', round(random.uniform(0, 20000), 2))
        emi_principal = override_fields.get('emi_principal', round(random.uniform(0, 20000), 2))
        acquired_balance = override_fields.get('acquired_balance', round(random.uniform(0, 2000), 2))
        cash_advance_balance = override_fields.get('cash_advance_balance', round(random.uniform(0, 5000), 2))
        # Dates
        creation_date = override_fields.get('creation_date')
        if not creation_date:
            try:
                creation_date_dt = datetime.now() - timedelta(days=random.randint(1, 365*5))
                creation_date = creation_date_dt.strftime('%Y-%m-%d')
            except Exception:
                creation_date = '2021-01-01'
        closed_date = override_fields.get('closed_date')
        if not closed_date and status == 'Closed':
            try:
                closed_date_dt = datetime.strptime(creation_date, '%Y-%m-%d') + timedelta(days=random.randint(30, 365*3))
                if closed_date_dt > datetime.now():
                    closed_date = None
                else:
                    closed_date = closed_date_dt.strftime('%Y-%m-%d')
            except Exception:
                closed_date = None
        excess_paid = override_fields.get('excess_paid', round(random.uniform(0, 500), 2))
        penalty = override_fields.get('penalty', round(random.uniform(0, 1000), 2))
        next_payment_due = override_fields.get('next_payment_due')
        if not next_payment_due:
            try:
                next_payment_due_dt = datetime.now() + timedelta(days=random.randint(1, 30))
                next_payment_due = next_payment_due_dt.strftime('%Y-%m-%d')
            except Exception:
                next_payment_due = None
        auto_debit = override_fields.get('auto_debit', random.choice([True, False]))
        mobile_last4 = override_fields.get('mobile_last4', str(random.randint(1000, 9999)))
        payment_network = override_fields.get('payment_network', random.choice(['Visa', 'Mastercard', 'Amex']))
        is_main_card = override_fields.get('is_main_card', random.choice([True, False]))
        expiry_date = override_fields.get('expiry_date')
        if not expiry_date:
            try:
                expiry_dt = datetime.now() + timedelta(days=random.randint(365, 365*5))
                expiry_date = expiry_dt.strftime('%m/%y')
            except Exception:
                expiry_date = '12/25'
        block_reason = override_fields.get('block_reason')
        if not block_reason and status == 'Blocked':
            block_reason = random.choice(['Fraud suspected', 'Overdue payment', 'Customer request'])
        # Max limit, daily spend
        max_limit = override_fields.get('max_limit', credit_limit + random.randint(0, 50000))
        max_daily_spend = override_fields.get('max_daily_spend', credit_limit)
        row = {
            'serial_number': serial_number,
            'customer_id': customer_id,
            'credit_card_number': credit_card_number,
            'card_type': card_type,
            'status': status,
            'billing_method': billing_method,
            'product_code': product_code,
            'card_currency': card_currency,
            'credit_limit': credit_limit,
            'outstanding_balance': outstanding_balance,
            'reward_points': reward_points,
            'reward_point_txns': reward_point_txns,
            'amount_overdue': amount_overdue,
            'overdue_since': overdue_since,
            'due_date': due_date,
            'min_amount_due': min_amount_due,
            'total_credited': total_credited,
            'total_debited': total_debited,
            'last_billing_date': last_billing_date,
            'last_payment_ref': last_payment_ref,
            'partition_key': partition_key,
            'active_emi_plans': active_emi_plans,
            'emi_outstanding': emi_outstanding,
            'emi_principal': emi_principal,
            'acquired_balance': acquired_balance,
            'cash_advance_balance': cash_advance_balance,
            'creation_date': creation_date,
            'closed_date': closed_date,
            'excess_paid': excess_paid,
            'penalty': penalty,
            'next_payment_due': next_payment_due,
            'auto_debit': auto_debit,
            'mobile_last4': mobile_last4,
            'payment_network': payment_network,
            'is_main_card': is_main_card,
            'expiry_date': expiry_date,
            'block_reason': block_reason,
            'max_limit': max_limit,
            'max_daily_spend': max_daily_spend
        }
        for k, v in override_fields.items():
            row[k] = v
        return row

    def _generate_credit_card_transactions_row(self, override_fields):
        # transaction_serial_number
        transaction_serial_number = override_fields.get('transaction_serial_number')
        if not transaction_serial_number:
            while True:
                candidate = f"TXN{random.randint(10000000,99999999)}"
                if candidate not in self.unique_sets['transaction_serial_number']:
                    transaction_serial_number = candidate
                    self.unique_sets['transaction_serial_number'].add(candidate)
                    break
        else:
            if transaction_serial_number not in self.unique_sets['transaction_serial_number']:
                self.unique_sets['transaction_serial_number'].add(transaction_serial_number)
        # serial_number (account)
        serial_number = override_fields.get('serial_number')
        if not serial_number:
            if self.reference_lists['credit_card_accounts']:
                serial_number = random.choice(self.reference_lists['credit_card_accounts'])
            else:
                serial_number = f"P{random.randint(100000,999999)}"
        # customer_id (from account)
        customer_id = override_fields.get('customer_id')
        if not customer_id:
            # Find customer_id from serial_number
            account_df = self.generated_data.get('credit_card_accounts')
            if account_df is not None and serial_number in account_df['serial_number'].values:
                customer_id = account_df[account_df['serial_number'] == serial_number]['customer_id'].values[0]
            else:
                customer_id = f"RIM{random.randint(10000000,99999999)}"
        # product_code
        product_code = override_fields.get('product_code')
        if not product_code:
            account_df = self.generated_data.get('credit_card_accounts')
            if account_df is not None and serial_number in account_df['serial_number'].values:
                product_code = account_df[account_df['serial_number'] == serial_number]['product_code'].values[0]
            else:
                product_code = 'VISA123'
        # Dates
        try:
            transaction_date_dt = datetime.now() - timedelta(days=random.randint(1, 365*2))
            transaction_date = override_fields.get('transaction_date', transaction_date_dt.strftime('%Y-%m-%d'))
            post_date_dt = transaction_date_dt + timedelta(days=random.randint(0, 5))
            post_date = override_fields.get('post_date', post_date_dt.strftime('%Y-%m-%d'))
        except Exception:
            transaction_date = '2023-01-01'
            post_date = '2023-01-02'
        # Amount
        transaction_amount = override_fields.get('transaction_amount')
        if transaction_amount is None:
            dist = self.data_distribution.get(('credit_card_transactions', 'transaction_amount'))
            if dist and dist['type'] == 'exponential':
                val = np.random.exponential(1/dist['lambda'])
                transaction_amount = float(np.clip(val, 1, 100000))
            else:
                transaction_amount = float(random.randint(1, 100000))
        final_amount = override_fields.get('final_amount', transaction_amount - random.uniform(0, 100))
        currency = override_fields.get('currency', random.choice(['INR', 'USD', 'AED']))
        settled_currency = override_fields.get('settled_currency', currency)
        txn_code = override_fields.get('txn_code', random.choice(['00', '05', '06', '20']))
        direction = override_fields.get('direction', random.choice(['Debit', 'Credit']))
        raw_txn_desc = override_fields.get('raw_txn_desc', self.faker.sentence(nb_words=4))
        # Status
        status = override_fields.get('status')
        if not status:
            dist = self.data_distribution.get(('credit_card_transactions', 'status'))
            if dist and dist['type'] == 'categorical':
                status = self._random_categorical(dist['parameters'])
            else:
                status = random.choice(['Success', 'Declined', 'Reversed'])
        # Points
        points_earned = override_fields.get('points_earned')
        if points_earned is None:
            points_earned = 0 if status == 'Declined' else random.randint(0, 50)
        # Online/International
        is_online = override_fields.get('is_online')
        if is_online is None:
            is_online = random.choice([True, False])
        local_international = override_fields.get('local_international')
        if not local_international:
            local_international = 'I' if random.random() < 0.15 else 'L'
        # Merchant
        merchant_id = override_fields.get('merchant_id', f"MID{random.randint(100000000,999999999)}")
        merchant_name = override_fields.get('merchant_name', random.choice(['Amazon', 'Flipkart', 'Swiggy', 'Uber', 'Zomato', 'BigBazaar']))
        city = override_fields.get('city', self.faker.city())
        country = override_fields.get('country', random.choice(['IN', 'AE', 'US']))
        mcc = override_fields.get('mcc', random.choice(['5411', '5812', '6011', '4111']))
        mcc_desc = override_fields.get('mcc_desc', random.choice(['Grocery', 'Dining', 'ATM', 'Transport']))
        txn_type = override_fields.get('txn_type', random.choice(['POS', 'Online', 'ATM', 'Reversal']))
        pos_entry_mode = override_fields.get('pos_entry_mode', random.choice(['021', '051', '081']))
        pos_condition_code = override_fields.get('pos_condition_code', random.choice(['00', '01', '08']))
        acquiring_inst_id = override_fields.get('acquiring_inst_id', random.choice(['HDFC0001', 'ICICI0002', 'SBI0003']))
        pos_terminal_id = override_fields.get('pos_terminal_id', f"POS{random.randint(1000,9999)}")
        cashback_amount = override_fields.get('cashback_amount', round(random.uniform(0, 500), 2))
        iso_msg_type = override_fields.get('iso_msg_type', random.choice(['0200', '0420', '0100']))
        orig_msg_type = override_fields.get('orig_msg_type', random.choice(['0100', '0200']))
        system = override_fields.get('system', random.choice(['IMOBILE_APP', 'POS_DEVICE', 'WEB_PORTAL']))
        reward_eligible = override_fields.get('reward_eligible', random.choice([True, False]))
        cleaned_desc = override_fields.get('cleaned_desc', merchant_name + " - " + mcc_desc)
        is_retail = override_fields.get('is_retail', random.choice([True, False]))
        row = {
            'transaction_serial_number': transaction_serial_number,
            'serial_number': serial_number,
            'customer_id': customer_id,
            'product_code': product_code,
            'transaction_date': transaction_date,
            'post_date': post_date,
            'transaction_amount': transaction_amount,
            'currency': currency,
            'settled_currency': settled_currency,
            'txn_code': txn_code,
            'direction': direction,
            'raw_txn_desc': raw_txn_desc,
            'final_amount': final_amount,
            'orig_msg_type': orig_msg_type,
            'merchant_id': merchant_id,
            'merchant_name': merchant_name,
            'city': city,
            'country': country,
            'mcc': mcc,
            'mcc_desc': mcc_desc,
            'txn_type': txn_type,
            'local_international': local_international,
            'is_online': is_online,
            'pos_entry_mode': pos_entry_mode,
            'pos_condition_code': pos_condition_code,
            'acquiring_inst_id': acquiring_inst_id,
            'pos_terminal_id': pos_terminal_id,
            'cashback_amount': cashback_amount,
            'iso_msg_type': iso_msg_type,
            'status': status,
            'points_earned': points_earned,
            'system': system,
            'reward_eligible': reward_eligible,
            'cleaned_desc': cleaned_desc,
            'is_retail': is_retail
        }
        for k, v in override_fields.items():
            row[k] = v
        return row

    def _generate_imobile_user_session_row(self, override_fields):
        # session_id
        session_id = override_fields.get('session_id')
        if not session_id:
            while True:
                candidate = f"sess_{self.faker.bothify(text='???###')}"
                if candidate not in self.unique_sets['session_id']:
                    session_id = candidate
                    self.unique_sets['session_id'].add(candidate)
                    break
        else:
            if session_id not in self.unique_sets['session_id']:
                self.unique_sets['session_id'].add(session_id)
        # customer_id
        customer_id = override_fields.get('customer_id')
        if not customer_id:
            if self.reference_lists['customer_info']:
                customer_id = random.choice(self.reference_lists['customer_info'])
            else:
                customer_id = f"RIM{random.randint(10000000,99999999)}"
        # session_start_time and end_time
        session_start_time = override_fields.get('session_start_time')
        session_end_time = override_fields.get('session_end_time')
        if not session_start_time or not session_end_time:
            try:
                now_ts = int(time.time())
                start_ts = random.randint(now_ts - 2*365*24*3600, now_ts)
                session_start_dt = datetime.fromtimestamp(start_ts)
                duration = random.randint(60, 3600)
                session_end_dt = session_start_dt + timedelta(seconds=duration)
                session_start_time = session_start_dt.strftime('%Y-%m-%d %H:%M')
                session_end_time = session_end_dt.strftime('%Y-%m-%d %H:%M')
            except Exception:
                session_start_time = '2023-01-01 09:00'
                session_end_time = '2023-01-01 09:30'
        # Channel
        channel = override_fields.get('channel')
        if not channel:
            dist = self.data_distribution.get(('imobile_user_session', 'channel'))
            if dist and dist['type'] == 'categorical':
                channel = self._random_categorical(dist['parameters'])
            else:
                channel = random.choice(['Mobile', 'Tablet', 'Web'])
        # Auth mode
        auth_mode = override_fields.get('auth_mode', random.choice(['Password', 'MPIN', 'Biometric', 'OTP']))
        outcome = override_fields.get('outcome', random.choice(['Success', 'Failed', 'Timeout']))
        fail_reason = override_fields.get('fail_reason')
        if not fail_reason and outcome != 'Success':
            fail_reason = random.choice(['Wrong MPIN', 'Biometric Mismatch', 'OTP Expired'])
        device_id = override_fields.get('device_id', self.faker.bothify(text='dev_??????'))
        device_type = override_fields.get('device_type', random.choice(['Android', 'iOS']))
        os_version = override_fields.get('os_version', random.choice(['iOS 17.3', 'Android 13', 'Android 12']))
        app_version = override_fields.get('app_version', f"v{random.randint(4,6)}.{random.randint(0,9)}.{random.randint(0,9)}")
        lat_long = override_fields.get('lat_long', f"{self.faker.latitude():.6f}, {self.faker.longitude():.6f}")
        network = override_fields.get('network', random.choice(['WiFi', '4G', '5G']))
        ip_address = override_fields.get('ip_address', self.faker.ipv4())
        duration_sec = override_fields.get('duration_sec')
        if not duration_sec:
            try:
                start_dt = datetime.strptime(session_start_time, '%Y-%m-%d %H:%M')
                end_dt = datetime.strptime(session_end_time, '%Y-%m-%d %H:%M')
                duration_sec = int((end_dt - start_dt).total_seconds())
                if duration_sec < 0:
                    duration_sec = 0
            except Exception:
                duration_sec = random.randint(60, 3600)
        first_login = override_fields.get('first_login', random.choice(['Y', 'N']))
        biometric_enabled = override_fields.get('biometric_enabled', random.choice(['Y', 'N']))
        push_notifications = override_fields.get('push_notifications', random.choice(['Y', 'N']))
        created_date = override_fields.get('created_date', session_start_time.split(' ')[0])
        last_updated = override_fields.get('last_updated', session_end_time)
        encrypted_pwd = override_fields.get('encrypted_pwd', uuid.uuid4().hex)
        hashed_mpin = override_fields.get('hashed_mpin', uuid.uuid4().hex)
        row = {
            'session_id': session_id,
            'customer_id': customer_id,
            'session_start_time': session_start_time,
            'session_end_time': session_end_time,
            'channel': channel,
            'auth_mode': auth_mode,
            'outcome': outcome,
            'fail_reason': fail_reason,
            'device_id': device_id,
            'device_type': device_type,
            'os_version': os_version,
            'app_version': app_version,
            'lat_long': lat_long,
            'network': network,
            'ip_address': ip_address,
            'duration_sec': duration_sec,
            'first_login': first_login,
            'biometric_enabled': biometric_enabled,
            'push_notifications': push_notifications,
            'created_date': created_date,
            'last_updated': last_updated,
            'encrypted_pwd': encrypted_pwd,
            'hashed_mpin': hashed_mpin
        }
        for k, v in override_fields.items():
            row[k] = v
        return row

    # ----------------- Business Rule Functions -----------------

    def _rule_unique_customer_id(self, df):
        # Remove duplicates, keep first
        return df.drop_duplicates(subset=['customer_id'])

    def _rule_valid_gender(self, df):
        valid = ['M', 'F', 'O']
        df.loc[~df['gender'].isin(valid), 'gender'] = 'O'
        return df

    def _rule_kyc_status_consistency(self, df):
        mask = (df['kyc_status'] == 'Verified') & (df['kyc_verified_flag'] != 1)
        df.loc[mask, 'kyc_verified_flag'] = 1
        return df

    def _rule_birth_date_validity(self, df):
        today = datetime.now()
        for idx, row in df.iterrows():
            try:
                bd = row['birth_date']
                if isinstance(bd, str):
                    bd_dt = datetime.strptime(bd, '%Y-%m-%d')
                else:
                    bd_dt = bd
                if bd_dt >= today:
                    # Set to 30 years ago
                    bd_dt = today - timedelta(days=30*365)
                    df.at[idx, 'birth_date'] = bd_dt.strftime('%Y-%m-%d')
                # Update age
                age = int((today - bd_dt).days // 365.25)
                df.at[idx, 'age'] = age
                if age < 26:
                    age_group = '18-25'
                elif age < 36:
                    age_group = '26-35'
                elif age < 51:
                    age_group = '36-50'
                else:
                    age_group = '51+'
                df.at[idx, 'age_group'] = age_group
            except Exception:
                df.at[idx, 'birth_date'] = '1980-01-01'
                df.at[idx, 'age'] = 30
                df.at[idx, 'age_group'] = '26-35'
        return df

    def _rule_annual_income_non_negative(self, df):
        df.loc[df['annual_income'] < 0, 'annual_income'] = 100000
        return df

    def _rule_unique_product_code(self, df):
        return df.drop_duplicates(subset=['product_code'])

    def _rule_active_flag_validity(self, df):
        df.loc[~df['active_flag'].isin(['Y', 'N']), 'active_flag'] = 'N'
        return df

    def _rule_product_date_range_validity(self, df):
        for idx, row in df.iterrows():
            try:
                start = datetime.strptime(str(row['start_date']), '%Y-%m-%d')
                end = datetime.strptime(str(row['end_date']), '%Y-%m-%d')
                if end < start:
                    # Set end = start + 1 year
                    end = start + timedelta(days=365)
                    df.at[idx, 'end_date'] = end.strftime('%Y-%m-%d')
            except Exception:
                df.at[idx, 'end_date'] = '2099-12-31'
        return df

    def _rule_interest_rate_range(self, df):
        df.loc[df['interest_rate'] < 0, 'interest_rate'] = 1.5
        df.loc[df['interest_rate'] > 10, 'interest_rate'] = 3.5
        return df

    def _rule_unique_serial_number(self, df):
        return df.drop_duplicates(subset=['serial_number'])

    def _rule_valid_customer_reference(self, df):
        valid_customers = set(self.reference_lists['customer_info'])
        df = df[df['customer_id'].isin(valid_customers)]
        return df

    def _rule_credit_limit_non_negative(self, df):
        df.loc[df['credit_limit'] < 0, 'credit_limit'] = 10000
        df.loc[df['max_limit'] < 0, 'max_limit'] = 10000
        return df

    def _rule_status_valid_values(self, df):
        valid = ['Active', 'Blocked', 'Closed']
        df.loc[~df['status'].isin(valid), 'status'] = 'Active'
        return df

    def _rule_account_date_consistency(self, df):
        for idx, row in df.iterrows():
            try:
                if pd.isnull(row['closed_date']) or row['closed_date'] in [None, '', 'nan']:
                    continue
                creation = datetime.strptime(str(row['creation_date']), '%Y-%m-%d')
                closed = datetime.strptime(str(row['closed_date']), '%Y-%m-%d')
                if closed <= creation:
                    closed = creation + timedelta(days=30)
                    df.at[idx, 'closed_date'] = closed.strftime('%Y-%m-%d')
            except Exception:
                df.at[idx, 'closed_date'] = None
        return df

    def _rule_unique_transaction_serial_number(self, df):
        return df.drop_duplicates(subset=['transaction_serial_number'])

    def _rule_valid_account_reference(self, df):
        valid_accounts = set(self.reference_lists['credit_card_accounts'])
        df = df[df['serial_number'].isin(valid_accounts)]
        return df

    def _rule_transaction_amount_non_negative(self, df):
        df.loc[df['transaction_amount'] < 0, 'transaction_amount'] = 1
        df.loc[df['final_amount'] < 0, 'final_amount'] = 1
        return df

    def _rule_transaction_status_valid(self, df):
        valid = ['Success', 'Declined', 'Reversed']
        df.loc[~df['status'].isin(valid), 'status'] = 'Success'
        return df

    def _rule_transaction_date_consistency(self, df):
        for idx, row in df.iterrows():
            try:
                tdate = datetime.strptime(str(row['transaction_date']), '%Y-%m-%d')
                pdate = datetime.strptime(str(row['post_date']), '%Y-%m-%d')
                if pdate < tdate:
                    pdate = tdate + timedelta(days=1)
                    df.at[idx, 'post_date'] = pdate.strftime('%Y-%m-%d')
            except Exception:
                df.at[idx, 'post_date'] = row['transaction_date']
        return df

    def _rule_unique_session_id(self, df):
        return df.drop_duplicates(subset=['session_id'])

    def _rule_valid_customer_reference_session(self, df):
        valid_customers = set(self.reference_lists['customer_info'])
        df = df[df['customer_id'].isin(valid_customers)]
        return df

    def _rule_session_time_consistency(self, df):
        for idx, row in df.iterrows():
            try:
                st = datetime.strptime(str(row['session_start_time']), '%Y-%m-%d %H:%M')
                et = datetime.strptime(str(row['session_end_time']), '%Y-%m-%d %H:%M')
                if et <= st:
                    et = st + timedelta(minutes=30)
                    df.at[idx, 'session_end_time'] = et.strftime('%Y-%m-%d %H:%M')
                    df.at[idx, 'duration_sec'] = int((et - st).total_seconds())
            except Exception:
                df.at[idx, 'session_end_time'] = row['session_start_time']
                df.at[idx, 'duration_sec'] = 1800
        return df

    def _rule_valid_channel(self, df):
        valid = ['Mobile', 'Tablet', 'Web']
        df.loc[~df['channel'].isin(valid), 'channel'] = 'Mobile'
        return df

    # ----------------- Utility Functions -----------------

    def _random_categorical(self, param_dict):
        vals = list(param_dict.keys())
        probs = list(param_dict.values())
        return np.random.choice(vals, p=probs)

    def _generate_luhn_card_number(self):
        # Generate a valid 16-digit card number using Luhn algorithm
        def luhn_checksum(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10
        while True:
            num = [4] + [random.randint(0,9) for _ in range(14)]
            check_digit = [0]
            for i in range(10):
                candidate = int(''.join(map(str, num + [i])))
                if luhn_checksum(candidate) == 0:
                    check_digit = [i]
                    break
            card_number = ''.join(map(str, num + check_digit))
            if len(card_number) == 16:
                return card_number

    def _ensure_all_columns(self, df, table_name):
        # Ensure all columns are present in the DataFrame
        columns = {
            'customer_info': [
                'customer_id','record_type','class_code','birth_date','city_of_birth','country_code','gender','language','nationality','profession','age','age_group','marital_status','city','address','created_date','closed_date','status','employer_id','employer_name','employer_sector','employer_name_clean','employer_name_redundant','class_code_desc','business_unit','segment','kyc_id_type','kyc_id_number','kyc_id_expiry','kyc_last_verified','kyc_status','kyc_verified_flag','imobile_registered','annual_income'
            ],
            'credit_card_products': [
                'product_code','product_name','card_type','secured','segmentation','currency','channel','bank','start_date','end_date','reward_program','default_credit_limit','annual_fee','interest_rate','billing_cycle_days','created_date','last_updated','active_flag'
            ],
            'credit_card_accounts': [
                'serial_number','customer_id','credit_card_number','card_type','status','billing_method','product_code','card_currency','credit_limit','outstanding_balance','reward_points','reward_point_txns','amount_overdue','overdue_since','due_date','min_amount_due','total_credited','total_debited','last_billing_date','last_payment_ref','partition_key','active_emi_plans','emi_outstanding','emi_principal','acquired_balance','cash_advance_balance','creation_date','closed_date','excess_paid','penalty','next_payment_due','auto_debit','mobile_last4','payment_network','is_main_card','expiry_date','block_reason','max_limit','max_daily_spend'
            ],
            'credit_card_transactions': [
                'transaction_serial_number','serial_number','customer_id','product_code','transaction_date','post_date','transaction_amount','currency','settled_currency','txn_code','direction','raw_txn_desc','final_amount','orig_msg_type','merchant_id','merchant_name','city','country','mcc','mcc_desc','txn_type','local_international','is_online','pos_entry_mode','pos_condition_code','acquiring_inst_id','pos_terminal_id','cashback_amount','iso_msg_type','status','points_earned','system','reward_eligible','cleaned_desc','is_retail'
            ],
            'imobile_user_session': [
                'session_id','customer_id','session_start_time','session_end_time','channel','auth_mode','outcome','fail_reason','device_id','device_type','os_version','app_version','lat_long','network','ip_address','duration_sec','first_login','biometric_enabled','push_notifications','created_date','last_updated','encrypted_pwd','hashed_mpin'
            ]
        }
        for col in columns[table_name]:
            if col not in df.columns:
                df[col] = np.nan
        return df[columns[table_name]]

if __name__ == '__main__':
    config = {
        "volume_percentage": 0.05,
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
        "seed": 42,
        "output_dir": "."
    }
    generator = SyntheticDataGenerator(config)
    generator.generate_all_data()
    generator.save_to_csv(config['output_dir'])
    print("Synthetic data generation complete. CSV files saved.")
