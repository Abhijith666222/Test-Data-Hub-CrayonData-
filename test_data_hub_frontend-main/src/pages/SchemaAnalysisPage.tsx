import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  Database, 
  ChevronDown,
  ChevronRight,
  Plus,
  Send,
  ArrowRight,
  ArrowLeft,
  Loader2,
  CheckCircle,
  AlertCircle,
  Info,
  Sparkles,
  BarChart3,
  Key,
  Hash,
  Link,
  Terminal,
  X,
  Settings
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useNotification } from '../context/NotificationContext';
import { apiService } from '../services/apiService';

const SchemaAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const { showSuccess, showError, showWarning } = useNotification();
  const [schemaAnalysis, setSchemaAnalysis] = useState<any>(null);
  const [testScenarios, setTestScenarios] = useState<any[]>([]);
  const [selectedScenarios, setSelectedScenarios] = useState<number[]>([]);
  const [expandedTables, setExpandedTables] = useState<string[]>([]);
  const [expandedScenarios, setExpandedScenarios] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingData, setIsGeneratingData] = useState(false);
  const [userPrompt, setUserPrompt] = useState('');
  const [showAddScenarios, setShowAddScenarios] = useState(false);
  const [showCrossTableRelationships, setShowCrossTableRelationships] = useState(false);
  const [showTestScenarios, setShowTestScenarios] = useState(false);
  const [showLibraryScenarios, setShowLibraryScenarios] = useState(false);
  const [showTestLibraryModal, setShowTestLibraryModal] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [isAnalysisInProgress, setIsAnalysisInProgress] = useState(false);
  const [showDataGenerationLoading, setShowDataGenerationLoading] = useState(false);
  const [dataGenerationStep, setDataGenerationStep] = useState(0);
  const [showScenarioCreationLoading, setShowScenarioCreationLoading] = useState(false);
  const [scenarioCreationStep, setScenarioCreationStep] = useState(0);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Demo schema analysis data for runs 2 and 3
  const getDemoSchemaAnalysis = async (runId: string) => {
    // Load actual schema analysis data from the run folders
    try {
      // Use the correct API endpoint to get schema analysis file content
      const apiUrl = `http://localhost:8000/runs/${runId}/files/schema/schema_analysis_results.json`;
      
      const response = await fetch(apiUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch schema analysis for run ${runId} - Status: ${response.status}`);
      }
      
      const result = await response.json();
      const content = result.content;
      
      if (content) {
        // Parse the JSON content
        const schemaAnalysis = JSON.parse(content);
        return schemaAnalysis;
      } else {
        throw new Error('Empty schema analysis content received');
      }
    } catch (error) {
      console.error('Failed to load demo schema analysis:', error);
      
      // Fallback to static demo data if file loading fails
      if (runId === '2') {
        // Run 2: Synthetic Data Generation demo
        return {
          summary: {
            total_tables: 5,
            total_business_rules: 35,
            total_test_scenarios: 135,
            analysis_mode: "full",
            journey_type: "synthetic_data_generation"
          },
          tables: [
            {
              table_name: "customer_info",
              primary_key: "customer_id",
              columns: [
                { name: "customer_id", type: "string", is_primary: true, is_nullable: false },
                { name: "type", type: "string", is_primary: false, is_nullable: false },
                { name: "birth_date", type: "date", is_primary: false, is_nullable: false },
                { name: "annual_income", type: "decimal", is_primary: false, is_nullable: false }
              ],
              business_rules: [
                { rule_name: "Customer ID Format", description: "Customer ID must follow RIM format", validation_logic: "customer_id LIKE 'RIM%'", error_message: "Invalid customer ID format" },
                { rule_name: "Age Validation", description: "Customer must be 18 or older", validation_logic: "birth_date <= CURRENT_DATE - INTERVAL '18 years'", error_message: "Customer must be 18 or older" },
                { rule_name: "Income Validation", description: "Annual income must be positive", validation_logic: "annual_income > 0", error_message: "Annual income must be positive" }
              ],
              test_scenarios: [
                { scenario_name: "New Customer Registration", description: "Test customer registration with valid data", priority: "HIGH" },
                { scenario_name: "High Net Worth Customer", description: "Test customer with high annual income", priority: "MEDIUM" },
                { scenario_name: "Minor Customer Rejection", description: "Test rejection of customers under 18", priority: "HIGH" }
              ]
            },
            {
              table_name: "credit_card_accounts",
              primary_key: "serial_number",
              columns: [
                { name: "serial_number", type: "string", is_primary: true, is_nullable: false },
                { name: "customer_id", type: "string", is_primary: false, is_nullable: false },
                { name: "credit_limit", type: "decimal", is_primary: false, is_nullable: false },
                { name: "outstanding_balance", type: "decimal", is_primary: false, is_nullable: false },
                { name: "status", type: "string", is_primary: false, is_nullable: false }
              ],
              business_rules: [
                { rule_name: "Credit Limit Validation", description: "Credit limit must be positive", validation_logic: "credit_limit > 0", error_message: "Invalid credit limit" },
                { rule_name: "Balance Limit", description: "Outstanding balance cannot exceed credit limit", validation_logic: "outstanding_balance <= credit_limit", error_message: "Balance exceeds credit limit" },
                { rule_name: "Valid Status", description: "Status must be one of: Active, Blocked, Closed", validation_logic: "status IN ('Active', 'Blocked', 'Closed')", error_message: "Invalid account status" }
              ],
              test_scenarios: [
                { scenario_name: "Account Creation", description: "Test credit card account creation", priority: "HIGH" },
                { scenario_name: "Credit Limit Increase", description: "Test credit limit increase scenario", priority: "MEDIUM" },
                { scenario_name: "Account Blocking", description: "Test account blocking due to fraud", priority: "HIGH" }
              ]
            }
          ],
          cross_table_relationships: [
            {
              from_table: "credit_card_accounts",
              to_table: "customer_info",
              relationship_type: "many-to-one",
              foreign_key: "customer_id",
              business_rules: ["Customer must exist before creating account"]
            },
            {
              from_table: "credit_card_transactions",
              to_table: "credit_card_accounts",
              relationship_type: "many-to-one",
              foreign_key: "serial_number",
              business_rules: ["Account must be active for transactions"]
            }
          ]
        };
      } else if (runId === '3') {
        // Run 3: Functional Test Scenarios demo
        return {
          summary: {
            total_tables: 5,
            total_business_rules: 28,
            total_test_scenarios: 95,
            analysis_mode: "schema_only",
            journey_type: "functional_test_scenarios"
          },
          tables: [
            {
              table_name: "customer_info",
              primary_key: "customer_id",
              columns: [
                { name: "customer_id", type: "string", is_primary: true, is_nullable: false },
                { name: "kyc_status", type: "string", is_primary: false, is_nullable: false },
                { name: "imobile_registered", type: "string", is_primary: false, is_nullable: false }
              ],
              business_rules: [
                { rule_name: "KYC Status Validation", description: "KYC status must be valid", validation_logic: "kyc_status IN ('Verified', 'Pending', 'Rejected')", error_message: "Invalid KYC status" },
                { rule_name: "Mobile Registration", description: "Mobile registration flag validation", validation_logic: "imobile_registered IN ('Y', 'N')", error_message: "Invalid mobile registration flag" }
              ],
              test_scenarios: [
                { scenario_name: "KYC Verification Process", description: "Test KYC verification workflow", priority: "HIGH" },
                { scenario_name: "Mobile App Registration", description: "Test mobile app registration process", priority: "MEDIUM" }
              ]
            },
            {
              table_name: "imobile_user_session",
              primary_key: "session_id",
              columns: [
                { name: "session_id", type: "string", is_primary: true, is_nullable: false },
                { name: "customer_id", type: "string", is_primary: false, is_nullable: false },
                { name: "session_start_time", type: "datetime", is_primary: false, is_nullable: false },
                { name: "session_end_time", type: "datetime", is_primary: false, is_nullable: true }
              ],
              business_rules: [
                { rule_name: "Session Time Validation", description: "Session end time must be after start time", validation_logic: "session_end_time > session_start_time", error_message: "Invalid session time" },
                { rule_name: "Active Session Limit", description: "Customer can have only one active session", validation_logic: "No overlapping active sessions", error_message: "Multiple active sessions not allowed" }
              ],
              test_scenarios: [
                { scenario_name: "User Login Session", description: "Test user login and session creation", priority: "HIGH" },
                { scenario_name: "Session Timeout", description: "Test session timeout after inactivity", priority: "MEDIUM" },
                { scenario_name: "Concurrent Login Prevention", description: "Test prevention of multiple active sessions", priority: "HIGH" }
              ]
            }
          ],
          cross_table_relationships: [
            {
              from_table: "imobile_user_session",
              to_table: "customer_info",
              relationship_type: "many-to-one",
              foreign_key: "customer_id",
              business_rules: ["Customer must be KYC verified for mobile sessions"]
            }
          ]
        };
      }
      
      // Default demo data
      return {
        summary: {
          total_tables: 5,
          total_business_rules: 30,
          total_test_scenarios: 100,
          analysis_mode: "full",
          journey_type: "synthetic_data_generation"
        },
        tables: [],
        cross_table_relationships: []
      };
    }
  };

   // Demo test scenarios data for runs 2 and 3
   const getDemoTestScenarios = async (runId: string) => {
     // Load actual test scenarios data from the run folders
     try {
       // Use the correct API endpoint to get test scenarios file content
       const apiUrl = `http://localhost:8000/runs/${runId}/test-scenarios`;
       
       const response = await fetch(apiUrl);
       if (!response.ok) {
         throw new Error(`Failed to fetch test scenarios for run ${runId} - Status: ${response.status}`);
       }
       
       const result = await response.json();
       
       if (result.scenarios && Array.isArray(result.scenarios)) {
         return result.scenarios;
       } else {
         throw new Error('Invalid test scenarios data received');
       }
     } catch (error) {
       console.error('Failed to load demo test scenarios:', error);
       
       // Fallback to static demo data if file loading fails
       if (runId === '2') {
         // Run 2: Synthetic Data Generation demo scenarios
         return [
           {
             id: 1,
             table_name: "customer_info",
             scenario_name: "High Credit Score Customer Profile",
             scenario_type: "positive",
             priority: "HIGH",
             description: "Generate synthetic data for customers with excellent credit scores (750+)",
             test_conditions: "credit_score >= 750 AND annual_income >= 50000 AND account_status = 'Active'",
             data_requirements: "Customer count: 1000, Credit limit range: 10000-50000, Transaction frequency: high"
           },
           {
             id: 2,
             table_name: "customer_info",
             scenario_name: "New Customer Onboarding",
             scenario_type: "positive",
             priority: "MEDIUM",
             description: "Test data for newly registered customers with minimal transaction history",
             test_conditions: "registration_date >= CURRENT_DATE - INTERVAL '30 days' AND transaction_count <= 5 AND kyc_status = 'Verified'",
             data_requirements: "Customer count: 500, Credit limit range: 1000-10000, Transaction frequency: low"
           },
           {
             id: 3,
             table_name: "credit_card_transactions",
             scenario_name: "Fraud Detection Testing",
             scenario_type: "negative",
             priority: "HIGH",
             description: "Synthetic data for testing fraud detection algorithms",
             test_conditions: "unusual_transaction_patterns = true AND multiple_locations = true AND high_transaction_amounts = true",
             data_requirements: "Customer count: 200, Fraud scenarios: stolen_card, identity_theft, merchant_fraud, Transaction amounts: 1000-10000"
           }
         ];
       } else if (runId === '3') {
         // Run 3: Functional Test Scenarios demo
         return [
           {
             id: 1,
             table_name: "imobile_user_session",
             scenario_name: "Mobile App Login Flow",
             scenario_type: "positive",
             priority: "HIGH",
             description: "Test the complete mobile app login and authentication process",
             test_conditions: "User enters valid credentials AND System validates KYC status AND Session is created and maintained",
             data_requirements: "Login successful for verified users, Session timeout after 30 minutes, Concurrent login prevention"
           },
           {
             id: 2,
             table_name: "customer_info",
             scenario_name: "KYC Verification Process",
             scenario_type: "positive",
             priority: "HIGH",
             description: "Test the Know Your Customer verification workflow",
             test_conditions: "Submit customer identification documents AND System processes and validates documents AND Update KYC status based on validation results",
             data_requirements: "KYC status updated correctly, Email notifications sent, Account restrictions applied for unverified users"
           },
           {
             id: 3,
             table_name: "credit_card_accounts",
             scenario_name: "Account Blocking Scenario",
             scenario_type: "negative",
             priority: "MEDIUM",
             description: "Test account blocking due to suspicious activity",
             test_conditions: "Detect suspicious transaction patterns AND Trigger fraud alert system AND Automatically block account",
             data_requirements: "Account status changed to 'Blocked', Transactions rejected, Customer notification sent, Manual review process initiated"
           }
         ];
       }
       
       // Default demo scenarios
       return [
         {
           id: 1,
           table_name: "customer_info",
           scenario_name: "Default Test Scenario",
           scenario_type: "positive",
           priority: "MEDIUM",
           description: "Default demo test scenario",
           test_conditions: "default_rule = true",
           data_requirements: "Customer count: 100"
         }
       ];
     }
   };

  useEffect(() => {
    if (!state.currentRun?.run_id) {
      navigate('/data-source');
      return;
    }
    loadSchemaAnalysis();
    loadTestScenarios();
  }, [state.currentRun, navigate]);

  useEffect(() => {
    // Auto-scroll to bottom of logs
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  useEffect(() => {
    // Connect to WebSocket for real-time logs
    if (isAnalysisInProgress) {
      const connectWebSocket = async () => {
        try {
          await apiService.connectWebSocket((message: any) => {
            if (message.type === 'log') {
              setLogs(prev => [...prev, message.data]);
            }
          });
        } catch (error) {
          console.error('Failed to connect to WebSocket:', error);
          // Add demo logs if WebSocket is not available
          const demoLogs = [
            '📋 STEP 1: Schema Discovery & Parsing',
            '2025-08-05 15:17:15,374 - INFO - 🔍 Scanning input schemas directory for CSV files...',
            '2025-08-05 15:17:15,380 - INFO - Successfully read schema for credit_card_accounts.csv',
            '2025-08-05 15:17:15,383 - INFO - Successfully read schema for credit_card_products.csv',
            '2025-08-05 15:17:15,386 - INFO - Successfully read schema for credit_card_transactions.csv',
            '2025-08-05 15:17:15,391 - INFO - Successfully read schema for customer_info.csv',
            '2025-08-05 15:17:15,393 - INFO - Successfully read schema for imobile_user_session.csv',
            '2025-08-05 15:17:15,394 - INFO - ✅ Discovered 5 schema files',
            '   📁 Found schemas: credit_card_accounts, credit_card_products, credit_card_transactions, customer_info, imobile_user_session',
            '',
            '🧠 STEP 2: AI Analysis Preparation',
            '2025-08-05 15:17:15,394 - INFO - 🤖 Preparing intelligent analysis prompt with schema context...',
            '2025-08-05 15:17:15,395 - INFO - 📝 Generated comprehensive prompt (31377 characters)',
            '',
            '🤖 STEP 3: AI-Powered Schema Analysis',
            '2025-08-05 15:17:15,396 - INFO - 🚀 Engaging OpenAI GPT-4 for intelligent schema analysis...',
            '   🔄 AI is analyzing table structures, relationships, and business logic...',
            '2025-08-05 15:17:45,123 - INFO - ✅ AI analysis completed successfully',
            '   ✅ AI analysis completed - insights extracted',
            '',
            '💾 STEP 4: Results Persistence',
            '2025-08-05 15:17:45,124 - INFO - 💾 Persisting AI-generated analysis results...',
            '2025-08-05 15:17:45,125 - INFO - 🎉 Schema analysis pipeline completed successfully',
            '   📊 Analysis results saved to schema directory'
          ];
          
          // Add demo logs with delays to simulate real-time updates
          demoLogs.forEach((log, index) => {
            setTimeout(() => {
              setLogs(prev => [...prev, log]);
            }, index * 1000); // Add each log with 1 second delay
          });
        }
      };
      
      connectWebSocket();
    }
  }, [isAnalysisInProgress]);

  useEffect(() => {
    // Poll for schema analysis results when analysis is in progress
    let pollInterval: NodeJS.Timeout;
    
    if (isAnalysisInProgress && state.currentRun?.run_id) {
      const runId = state.currentRun.run_id; // Store run_id to avoid null checks inside interval
      pollInterval = setInterval(async () => {
        try {
          const files = await apiService.getRunFiles(runId);
          if (files?.data?.files?.schema) {
            const schemaFile = files.data.files.schema.find((f: any) => f.name.includes('schema_analysis_results'));
            if (schemaFile) {
              // Schema analysis completed, load the results
              const content = await apiService.downloadFile(
                runId,
                'schema',
                schemaFile.name
              );
              if (content?.content) {
                const analysis = JSON.parse(content.content);
                setSchemaAnalysis(analysis);
                dispatch({ type: 'SET_SCHEMA_ANALYSIS', payload: analysis });
                setIsAnalysisInProgress(false);
                setLogs(prev => [...prev, '✅ Schema analysis completed successfully!']);
              }
            }
          }
        } catch (error) {
          console.error('Failed to poll for schema analysis results:', error);
        }
      }, 5000); // Poll every 5 seconds
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [isAnalysisInProgress, state.currentRun?.run_id, dispatch]);

  const loadSchemaAnalysis = async () => {
    if (!state.currentRun?.run_id) return;
    
    // Check if this is a demo mode run (runs 2 and 3)
    const isDemoRun = state.currentRun.run_id === '2' || state.currentRun.run_id === '3';
    
    setIsLoading(true);
    try {
      if (isDemoRun) {
        // Demo mode: Load existing run data without calling APIs
        
        // Load demo schema analysis data based on run
        const demoAnalysis = await getDemoSchemaAnalysis(state.currentRun.run_id);
        setSchemaAnalysis(demoAnalysis);
        dispatch({ type: 'SET_SCHEMA_ANALYSIS', payload: demoAnalysis });
        setIsAnalysisInProgress(false);
        setIsLoading(false);
        return;
      }
      
      // Real mode: Call APIs to get actual data
      console.log('Loading schema analysis for run:', state.currentRun.run_id);
      
      // First, load the run configuration to understand the product type
      console.log('Loading run configuration...');
      const runConfig = await loadRunConfig(state.currentRun.run_id);
      if (runConfig) {
        console.log('Run configuration loaded:', runConfig);
        console.log('Run configuration data:', runConfig.data);
        console.log('Run configuration structure:', JSON.stringify(runConfig, null, 2));
        
        // Store the run configuration in the app context so it's available for the generate button
        dispatch({ type: 'SET_RUN_CONFIG', payload: runConfig });
      } else {
        console.warn('No run configuration found');
      }
      
      const files = await apiService.getRunFiles(state.currentRun.run_id);
      console.log('Files response:', files);
      console.log('Files structure:', files?.data?.files);
      console.log('Schema files:', files?.data?.files?.schema);
      
              if (files?.data?.files?.schema) {
          const schemaFile = files.data.files.schema.find((f: any) => f.name.includes('schema_analysis_results'));
        console.log('Found schema file:', schemaFile);
        
        if (schemaFile) {
          console.log('Downloading schema file:', schemaFile.name);
          const content = await apiService.downloadFile(
            state.currentRun.run_id,
            'schema',
            schemaFile.name
          );
          console.log('Downloaded content:', content);
          
          if (content?.content) {
            console.log('Parsing JSON content...');
            try {
              const analysis = JSON.parse(content.content);
              console.log('Parsed analysis:', analysis);
              setSchemaAnalysis(analysis);
              dispatch({ type: 'SET_SCHEMA_ANALYSIS', payload: analysis });
              setIsAnalysisInProgress(false);
              console.log('Schema analysis loaded successfully');
            } catch (parseError: unknown) {
              console.error('JSON parsing failed:', parseError);
              console.error('Content length:', content.content.length);
              console.error('Content preview (first 500 chars):', content.content.substring(0, 500));
              console.error('Content around error position:');
              
              // Show content around the error position
              const errorMessage = parseError instanceof Error ? parseError.message : String(parseError);
              const errorPosition = errorMessage.match(/position (\d+)/);
              if (errorPosition) {
                const pos = parseInt(errorPosition[1]);
                const start = Math.max(0, pos - 100);
                const end = Math.min(content.content.length, pos + 100);
                console.error('Content around position', pos, ':', content.content.substring(start, end));
                console.error('Error at position', pos, ':', content.content.charAt(pos));
              }
              
              // Show the problematic line
              const lines = content.content.split('\n');
              console.error('Total lines:', lines.length);
              if (lines.length > 0) {
                console.error('Line 524:', lines[523]); // 0-indexed, so line 524 is at index 523
                console.error('Line 525:', lines[524]);
                console.error('Line 526:', lines[525]);
              }
              
              setIsAnalysisInProgress(true);
              setLogs([
                '🧠 AI-Powered Schema Analysis Engine',
                `📊 Run ID: ${state.currentRun.run_id}`,
                '============================================================',
                '❌ JSON Parsing Error',
                `Error: ${errorMessage}`,
                'Please check the schema_analysis_results.json file for syntax errors.'
              ]);
            }
          } else if (content?.data?.content) {
            // Handle the case where content is nested in data property
            console.log('Parsing JSON content from data.content...');
            try {
              const analysis = JSON.parse(content.data.content);
              console.log('Parsed analysis:', analysis);
              setSchemaAnalysis(analysis);
              dispatch({ type: 'SET_SCHEMA_ANALYSIS', payload: analysis });
              setIsAnalysisInProgress(false);
              console.log('Schema analysis loaded successfully');
            } catch (parseError: unknown) {
              console.error('JSON parsing failed:', parseError);
              console.error('Content length:', content.data.content.length);
              console.error('Content preview (first 500 chars):', content.data.content.substring(0, 500));
              console.error('Content around error position:');
              
              // Show content around the error position
              const errorMessage = parseError instanceof Error ? parseError.message : String(parseError);
              const errorPosition = errorMessage.match(/position (\d+)/);
              if (errorPosition) {
                const pos = parseInt(errorPosition[1]);
                const start = Math.max(0, pos - 100);
                const end = Math.min(content.data.content.length, pos + 100);
                console.error('Content around position', pos, ':', content.data.content.substring(start, end));
                console.error('Error at position', pos, ':', content.data.content.charAt(pos));
              }
              
              // Show the problematic line
              const lines = content.data.content.split('\n');
              console.error('Total lines:', lines.length);
              if (lines.length > 0) {
                console.error('Line 524:', lines[523]); // 0-indexed, so line 524 is at index 523
                console.error('Line 525:', lines[524]);
                console.error('Line 526:', lines[525]);
              }
              
              setIsAnalysisInProgress(true);
              setLogs([
                '🧠 AI-Powered Schema Analysis Engine',
                `📊 Run ID: ${state.currentRun.run_id}`,
                '============================================================',
                '❌ JSON Parsing Error',
                `Error: ${errorMessage}`,
                'Please check the schema_analysis_results.json file for syntax errors.'
              ]);
            }
          } else {
            console.error('No content in downloaded file');
            console.error('Content structure:', content);
            setIsAnalysisInProgress(true);
          }
        } else {
          console.warn('No schema analysis results file found');
          // No schema file found - analysis might be in progress
          setIsAnalysisInProgress(true);
          setLogs([
            '🧠 AI-Powered Schema Analysis Engine',
            `📊 Run ID: ${state.currentRun.run_id}`,
            '============================================================',
            '🤖 Initializing intelligent schema analysis...',
            '🔍 Scanning input schemas directory for CSV files...'
          ]);
        }
      } else {
        console.warn('No schema files found in response');
        console.warn('Files response structure:', files);
        // No schema file found - analysis might be in progress
        setIsAnalysisInProgress(true);
        setLogs([
          '🧠 AI-Powered Schema Analysis Engine',
          `📊 Run ID: ${state.currentRun.run_id}`,
          '============================================================',
          '🤖 Initializing intelligent schema analysis...',
          '🔍 Scanning input schemas directory for CSV files...'
        ]);
      }
    } catch (error) {
      console.error('Failed to load schema analysis:', error);
      setIsAnalysisInProgress(true);
      setLogs([
        '🧠 AI-Powered Schema Analysis Engine',
        `📊 Run ID: ${state.currentRun.run_id}`,
        '============================================================',
        '🤖 Initializing intelligent schema analysis...',
        '🔍 Scanning input schemas directory for CSV files...'
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadRunConfig = async (runId: string) => {
    try {
      const configFile = await apiService.getRunConfig(runId);
      if (configFile) {
        return configFile;
      }
      console.warn(`No run_config.json found for run ${runId}`);
      return null;
    } catch (error) {
      console.error(`Failed to load run_config.json for run ${runId}:`, error);
      return null;
    }
  };

  const loadTestScenarios = async () => {
    if (!state.currentRun?.run_id) return;
    
    // Check if this is a demo mode run
    const isDemoRun = state.currentRun.run_id === '2' || state.currentRun.run_id === '3';
    
    if (isDemoRun) {
      // Demo mode: Load demo test scenarios
      
      const demoScenarios = await getDemoTestScenarios(state.currentRun.run_id);
      setTestScenarios(demoScenarios);
      dispatch({ type: 'SET_TEST_SCENARIOS', payload: demoScenarios });
      return;
    }
    
    // Real mode: Call API to get actual test scenarios
    try {
      console.log('Loading test scenarios for run:', state.currentRun.run_id);
      const scenarios = await apiService.getTestScenarios(state.currentRun.run_id);
      console.log('Test scenarios response:', scenarios);
      
      if (scenarios?.scenarios) {
        console.log('Setting test scenarios:', scenarios.scenarios);
        setTestScenarios(scenarios.scenarios);
        dispatch({ type: 'SET_TEST_SCENARIOS', payload: scenarios.scenarios });
      } else {
        console.warn('No scenarios found in response:', scenarios);
      }
    } catch (error: any) {
      console.error('Failed to load test scenarios:', error);
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
    }
  };

  const toggleTableExpansion = (tableName: string) => {
    setExpandedTables(prev => 
      prev.includes(tableName) 
        ? prev.filter(t => t !== tableName)
        : [...prev, tableName]
    );
  };

  const toggleScenarioExpansion = (scenarioId: string) => {
    setExpandedScenarios(prev => 
      prev.includes(scenarioId) 
        ? prev.filter(s => s !== scenarioId)
        : [...prev, scenarioId]
    );
  };

  const toggleScenarioSelection = (scenarioId: number) => {
    setSelectedScenarios(prev => 
      prev.includes(scenarioId)
        ? prev.filter(s => s !== scenarioId)
        : [...prev, scenarioId]
    );
  };

  const handleAddTestScenarios = async () => {
    if (!userPrompt.trim()) {
      showWarning('Warning', 'Please enter a prompt for generating test scenarios.');
      return;
    }

    // Show loading popup
    setShowScenarioCreationLoading(true);
    setScenarioCreationStep(0);
    
    const steps = [
      'Analyzing user input',
      'Evaluating tables for this criteria',
      'Applying test scenarios'
    ];
    
    try {
      // Get current run ID from context
      const currentRunId = state.currentRun?.run_id;
      if (!currentRunId) {
        showError('Error', 'No active run found. Please start a new run first.');
        setShowScenarioCreationLoading(false);
        return;
      }

      // Get the first table from schema analysis for now (can be enhanced to let user choose)
      if (!schemaAnalysis?.tables || schemaAnalysis.tables.length === 0) {
        showError('Error', 'No tables found in schema analysis. Please run schema analysis first.');
        setShowScenarioCreationLoading(false);
        return;
      }

      const targetTable = schemaAnalysis.tables[0]; // Use first table for now
      
      // Simulate AI processing steps
      for (let i = 0; i < steps.length; i++) {
        setScenarioCreationStep(i);
        await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second per step
      }
      
      // Call the real backend API
      const response = await apiService.generateScenarioFromPrompt(
        currentRunId,
        targetTable.table_name,
        userPrompt
      );
      
      console.log('🔍 Backend response received:', response);
      
      // Extract data from response (backend wraps in 'data' property)
      const responseData = response.data || response;
      
      if (responseData.business_rules || responseData.test_scenarios) {
        // Create new scenarios from the AI-generated content
        const newScenarios: any[] = [];
        
        // Add business rules as scenarios if generated
        if (responseData.business_rules && responseData.business_rules.length > 0) {
          responseData.business_rules.forEach((rule: any) => {
            newScenarios.push({
              id: Date.now() + Math.random(),
              table_name: rule.table_name,
              scenario_name: `Business Rule: ${rule.rule_name}`,
              scenario_type: 'business_logic',
              priority: rule.severity || 'MEDIUM',
              description: rule.description,
              test_conditions: rule.validation_logic,
              expected_behavior: rule.error_message,
              data_requirements: `Data that validates: ${rule.description}`
            });
          });
        }
        
        // Add test scenarios if generated
        if (responseData.test_scenarios && responseData.test_scenarios.length > 0) {
          responseData.test_scenarios.forEach((scenario: any) => {
            newScenarios.push({
              id: Date.now() + Math.random(),
              table_name: scenario.table_name,
              scenario_name: scenario.scenario_name,
              scenario_type: scenario.scenario_type,
              priority: scenario.priority || 'MEDIUM',
              description: scenario.description,
              test_conditions: scenario.test_conditions,
              expected_behavior: scenario.expected_behavior,
              data_requirements: scenario.data_requirements
            });
          });
        }
        
        // Add to test scenarios list
        setTestScenarios([...testScenarios, ...newScenarios]);
        
        // Refresh schema analysis to include the new content
        try {
          console.log('🔄 Refreshing schema analysis to include new content...');
          const updatedFiles = await apiService.getRunFiles(currentRunId);
          if (updatedFiles?.data?.files?.schema) {
            const schemaFile = updatedFiles.data.files.schema.find((f: any) => 
              f.filename === 'schema_analysis_results.json'
            );
            if (schemaFile) {
              const schemaContent = await apiService.downloadFile(
                currentRunId, 
                'schema', 
                'schema_analysis_results.json'
              );
              if (schemaContent?.data?.content) {
                const updatedSchema = JSON.parse(schemaContent.data.content);
                setSchemaAnalysis(updatedSchema);
                dispatch({ type: 'SET_SCHEMA_ANALYSIS', payload: updatedSchema });
                console.log('✅ Schema analysis refreshed with new content');
              }
            }
          }
        } catch (refreshError) {
          console.warn('⚠️ Could not refresh schema analysis:', refreshError);
        }
        
        // Show success message
        showSuccess('Success', `Generated ${newScenarios.length} new test scenarios from your prompt!`);
        
        // Clear the form
        setUserPrompt('');
        setShowAddScenarios(false);
        
      } else {
        showWarning('Warning', 'No test scenarios were generated from your prompt. Please try a different description.');
      }
      
    } catch (error) {
      console.error('Error generating test scenario:', error);
      showError('Error', `Failed to generate test scenario: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setShowScenarioCreationLoading(false);
    }
  };

  const handleGenerateData = async () => {
    console.log('🔍 handleGenerateData called');
    console.log('Current state:', {
      currentRun: state.currentRun,
      selectedProduct: state.selectedProduct,
      runConfig: state.runConfig,
      isDemoMode: state.isDemoMode,
      selectedScenarios: selectedScenarios
    });
    
    // Check if this is run 2 or 3 (sample data runs)
    const isSampleDataRun = state.currentRun?.run_id === '2' || state.currentRun?.run_id === '3';
    console.log('Is sample data run:', isSampleDataRun);
    
    // Get the current run context
    const currentRunId = state.currentRun?.run_id;
    
    // Determine product type from run configuration or selected product
    let productType = state.selectedProduct?.id;
    if (!productType && state.runConfig) {
      // Handle both direct config and nested data.config structures
      const config = state.runConfig.config || state.runConfig.data?.config;
      productType = config?.product_type;
      console.log('Product type determined from run config:', productType);
      console.log('Run config structure:', state.runConfig);
      console.log('Config object:', config);
    }
    
    if (!currentRunId) {
      showError('Error', 'No run context found. Please ensure you are on a valid run page.');
      return;
    }
    
    console.log('Current run context:', {
      runId: currentRunId,
      product: productType,
      isDemoMode: state.isDemoMode,
      runConfig: state.runConfig
    });
    
    // For synthetic data generation, no scenario selection is required
    if (productType === 'synthetic-data-generation') {
      console.log('Processing synthetic data generation - no scenarios required');
      
      // Check if this is a sample data run
      if (isSampleDataRun) {
        console.log('Processing sample data run...');
        // For sample data runs, show loading for longer time with continuous step flow
        setShowDataGenerationLoading(true);
        setDataGenerationStep(0);
        
        const steps = [
          'Understanding your data',
          'Understanding the schema',
          'Applying relational logics',
          'Applying test scenarios'
        ];
        
        // Show continuous flow for 4-5 seconds
        const totalDuration = 4500; // 4.5 seconds
        const stepDuration = totalDuration / steps.length;
        
        for (let i = 0; i < steps.length; i++) {
          setDataGenerationStep(i);
          await new Promise(resolve => setTimeout(resolve, stepDuration));
        }
        
        // Continue cycling through steps for the remaining time
        const remainingTime = 2000; // 2 more seconds
        const cycleDuration = remainingTime / steps.length;
        
        for (let cycle = 0; cycle < 2; cycle++) {
          for (let i = 0; i < steps.length; i++) {
            setDataGenerationStep(i);
            await new Promise(resolve => setTimeout(resolve, cycleDuration));
          }
        }
        
        setTimeout(() => {
          setShowDataGenerationLoading(false);
          navigate('/data-generation');
        }, 500);
      } else {
        // For new synthetic data generation runs
        console.log('Processing new synthetic data generation run...');
        setShowDataGenerationLoading(true);
        setDataGenerationStep(0);
        
        setIsGeneratingData(true);
        try {
          console.log('Triggering Synthetic Data Generator Agent for run:', currentRunId);
          
          const steps = [
            'Initializing Synthetic Data Generator',
            'Analyzing schema structure',
            'Generating synthetic data',
            'Applying business rules and constraints'
          ];
          
          // Show loading steps
          for (let i = 0; i < steps.length; i++) {
            setDataGenerationStep(i);
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
          
          // Call the synthetic data generation API
          console.log('Calling generateSyntheticData API...');
          const result = await apiService.generateSyntheticData(
            currentRunId,
            {
              default_records: 1000,
              priority_multipliers: {
                CRITICAL: 2.0,
                HIGH: 1.5,
                MEDIUM: 1.0,
                LOW: 0.5
              }
            }
          );
          
          console.log('API response:', result);
          
          if (result?.run_id) {
            console.log('Synthetic data generation started successfully:', result);
            
            // Continue showing loading state and poll for completion
            setDataGenerationStep(4); // Show "Waiting for completion" step
            
            // Poll for data generation completion
            let isComplete = false;
            let attempts = 0;
            const maxAttempts = 60; // 5 minutes max (5 seconds * 60)
            
            while (!isComplete && attempts < maxAttempts) {
              await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds between checks
              attempts++;
              
              try {
                // Check if synthetic data files are available
                const files = await apiService.getRunFiles(currentRunId);
                if (files?.files?.synthetic_data && files.files.synthetic_data.length > 0) {
                  console.log('Synthetic data generation completed!');
                  isComplete = true;
                } else if (files?.data?.files?.synthetic_data && files.data.files.synthetic_data.length > 0) {
                  console.log('Synthetic data generation completed!');
                  isComplete = true;
                } else {
                  console.log(`Waiting for data generation... Attempt ${attempts}/${maxAttempts}`);
                  // Update step to show progress
                  setDataGenerationStep(4 + (attempts % 3)); // Cycle through steps 4-6
                }
              } catch (error) {
                console.log('Error checking completion status:', error);
                // Continue polling
              }
            }
            
            if (isComplete) {
              setShowDataGenerationLoading(false);
              navigate('/data-generation');
            } else {
              throw new Error('Data generation timed out after 5 minutes');
            }
          } else {
            throw new Error('Failed to start synthetic data generation');
          }
          
        } catch (error) {
          console.error('Failed to generate data:', error);
          setShowDataGenerationLoading(false);
          showError('Error', `Failed to start data generation: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
          setIsGeneratingData(false);
        }
      }
      
    } else if (productType === 'functional-test-scenarios') {
      // For functional test scenarios, use synthetic data generation with schema
      console.log('Processing functional test scenarios - using synthetic data generation with schema');
      
      // Check if this is a sample data run
      if (isSampleDataRun) {
        console.log('Processing sample data run for test scenarios...');
        // For sample data runs, show loading for longer time with continuous step flow
        setShowDataGenerationLoading(true);
        setDataGenerationStep(0);
        
        const steps = [
          'Understanding your data',
          'Understanding the schema',
          'Applying relational logics',
          'Applying test scenarios'
        ];
        
        // Show continuous flow for 4-5 seconds
        const totalDuration = 4500; // 4.5 seconds
        const stepDuration = totalDuration / steps.length;
        
        for (let i = 0; i < steps.length; i++) {
          setDataGenerationStep(i);
          await new Promise(resolve => setTimeout(resolve, stepDuration));
        }
        
        // Continue cycling through steps for the remaining time
        const remainingTime = 2000; // 2 more seconds
        const cycleDuration = remainingTime / steps.length;
        
        for (let cycle = 0; cycle < 2; cycle++) {
          for (let i = 0; i < steps.length; i++) {
            setDataGenerationStep(i);
            await new Promise(resolve => setTimeout(resolve, cycleDuration));
          }
        }
        
        setTimeout(() => {
          setShowDataGenerationLoading(false);
          navigate('/data-generation');
        }, 500);
      } else {
        // For new test scenario runs
        console.log('Processing new test scenario run...');
        setShowDataGenerationLoading(true);
        setDataGenerationStep(0);
        
        setIsGeneratingData(true);
        try {
          console.log('Triggering Synthetic Data Generator Agent for run:', currentRunId);
          
          const steps = [
            'Initializing Synthetic Data Generator',
            'Processing schema analysis',
            'Generating synthetic data',
            'Applying business rules and constraints'
          ];
          
          // Show loading steps
          for (let i = 0; i < steps.length; i++) {
            setDataGenerationStep(i);
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
          
          // Call the test scenario data generation API
          const config = {
            default_records: 100,
            priority_multipliers: {
              CRITICAL: 2.0,
              HIGH: 1.5,
              MEDIUM: 1.0,
              LOW: 0.5
            }
          };

          console.log('🔄 Calling generateTestScenarios API with:', {
            runId: currentRunId,
            selectedScenarios: [],
            config
          });

          const result = await apiService.generateTestScenarios(
            currentRunId,
            [], // Empty array - will use scenarios from schema
            config
          );

          console.log('🔍 API response received:', result);
          
          // Extract data from response (backend wraps in 'data' property)
          const responseData = result.data || result;
          
          if (responseData?.run_id) {
            console.log('Synthetic data generation started successfully:', responseData);
            
            // Continue showing loading state and poll for completion
            setDataGenerationStep(4); // Show "Waiting for completion" step
            
            // Poll for data generation completion
            let isComplete = false;
            let attempts = 0;
            const maxAttempts = 60; // 5 minutes max (5 seconds * 60)
            
            while (!isComplete && attempts < maxAttempts) {
              await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds between checks
              attempts++;
              
              try {
                // Check if synthetic data files are available
                const files = await apiService.getRunFiles(currentRunId);
                if (files?.files?.synthetic_data && files.files.synthetic_data.length > 0) {
                  console.log('Synthetic data generation completed!');
                  isComplete = true;
                } else if (files?.data?.files?.synthetic_data && files.data.files.synthetic_data.length > 0) {
                  console.log('Synthetic data generation completed!');
                  isComplete = true;
                } else {
                  console.log(`Waiting for data generation... Attempt ${attempts}/${maxAttempts}`);
                  // Update step to show progress
                  setDataGenerationStep(4 + (attempts % 3)); // Cycle through steps 4-6
                }
              } catch (error) {
                console.log('Error checking completion status:', error);
                // Continue polling
              }
            }
            
            if (isComplete) {
              setShowDataGenerationLoading(false);
              navigate('/data-generation');
            } else {
              throw new Error('Data generation timed out after 5 minutes');
            }
          } else {
            throw new Error('Failed to start synthetic data generation');
          }
          
        } catch (error) {
          console.error('Failed to generate data:', error);
          setShowDataGenerationLoading(false);
          showError('Error', `Failed to start data generation: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
          setIsGeneratingData(false);
        }
      }
      
    } else {
      // Fallback: No product selected or unknown product
      console.log('No product selected or unknown product, using fallback behavior');
      
      if (selectedScenarios.length === 0) {
        showWarning('Warning', 'Please select at least one test scenario to generate data for.');
        return;
      }
      
      // Check if this is a sample data run
      if (isSampleDataRun) {
        console.log('Processing sample data run with fallback...');
        // For sample data runs, show loading for longer time with continuous step flow
        setShowDataGenerationLoading(true);
        setDataGenerationStep(0);
        
        const steps = [
          'Understanding your data',
          'Understanding the schema',
          'Applying relational logics',
          'Applying test scenarios'
        ];
        
        // Show continuous flow for 4-5 seconds
        const totalDuration = 4500; // 4.5 seconds
        const stepDuration = totalDuration / steps.length;
        
        for (let i = 0; i < steps.length; i++) {
          setDataGenerationStep(i);
          await new Promise(resolve => setTimeout(resolve, stepDuration));
        }
        
        // Continue cycling through steps for the remaining time
        const remainingTime = 2000; // 2 more seconds
        const cycleDuration = remainingTime / steps.length;
        
        for (let cycle = 0; cycle < 2; cycle++) {
          for (let i = 0; i < steps.length; i++) {
            setDataGenerationStep(i);
            await new Promise(resolve => setTimeout(resolve, cycleDuration));
          }
        }
        
        setTimeout(() => {
          setShowDataGenerationLoading(false);
          navigate('/data-generation');
        }, 500);
      } else {
        // For new runs with fallback
        console.log('Processing new run with fallback test scenario generation...');
        setShowDataGenerationLoading(true);
        setDataGenerationStep(0);
        
        setIsGeneratingData(true);
        try {
          const config = {
            default_records: 100,
            priority_multipliers: {
              CRITICAL: 2.0,
              HIGH: 1.5,
              MEDIUM: 1.0,
              LOW: 0.5
            }
          };

          console.log('🔄 Calling generateTestScenarios API with:', {
            runId: currentRunId,
            selectedScenarios: [],
            config
          });

          const result = await apiService.generateTestScenarios(
            currentRunId,
            [], // Empty array - will use scenarios from schema
            config
          );

          console.log('🔍 API response received:', result);
          
          // Extract data from response (backend wraps in 'data' property)
          const responseData = result.data || result;
          
          if (responseData?.run_id) {
            console.log('Synthetic data generation started successfully:', responseData);
            
            // Continue showing loading state and poll for completion
            setDataGenerationStep(4); // Show "Waiting for completion" step
            
            // Poll for data generation completion
            let isComplete = false;
            let attempts = 0;
            const maxAttempts = 60; // 5 minutes max (5 seconds * 60)
            
            while (!isComplete && attempts < maxAttempts) {
              await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds between checks
              attempts++;
              
              try {
                // Check if synthetic data files are available
                const files = await apiService.getRunFiles(currentRunId);
                if (files?.files?.synthetic_data && files.files.synthetic_data.length > 0) {
                  console.log('Synthetic data generation completed!');
                  isComplete = true;
                } else if (files?.data?.files?.synthetic_data && files.data.files.synthetic_data.length > 0) {
                  console.log('Synthetic data generation completed!');
                  isComplete = true;
                } else {
                  console.log(`Waiting for data generation... Attempt ${attempts}/${maxAttempts}`);
                  // Update step to show progress
                  setDataGenerationStep(4 + (attempts % 3)); // Cycle through steps 4-6
                }
              } catch (error) {
                console.log('Error checking completion status:', error);
                // Continue polling
              }
            }
            
            if (isComplete) {
              setShowDataGenerationLoading(false);
              navigate('/data-generation');
            } else {
              throw new Error('Data generation timed out after 5 minutes');
            }
          } else {
            throw new Error('Failed to start data generation');
          }
          
        } catch (error) {
          console.error('Failed to generate data:', error);
          setShowDataGenerationLoading(false);
          showError('Error', `Failed to start data generation: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
          setIsGeneratingData(false);
        }
      }
    }
  };

  const renderTableAnalysis = (tableName: string, tableData: any) => {
    const isExpanded = expandedTables.includes(tableName);
    
    return (
      <div key={tableName} className="border border-windows-200 rounded-lg mb-4">
        <div 
          className="p-4 bg-windows-50 border-b border-windows-200 cursor-pointer hover:bg-windows-100 transition-colors duration-200"
          onClick={() => toggleTableExpansion(tableName)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Database className="h-5 w-5 text-accent-600" />
              <h3 className="font-semibold text-windows-900">{tableName}</h3>
              <div className="flex items-center space-x-2">
                <span className="badge-windows badge-windows-success">
                  PK: {tableData.primary_key}
                </span>
                <span className="badge-windows badge-windows-info">
                  {tableData.business_rules?.length || 0} rules
                </span>
                <span className="badge-windows badge-windows-accent">
                  {tableData.test_scenarios?.length || 0} scenarios
                </span>
              </div>
            </div>
            {isExpanded ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
          </div>
        </div>
        
        {isExpanded && (
          <div className="p-4 bg-white">
            <div className="space-y-6">
              {/* Primary Key */}
              {tableData.primary_key && (
                <div>
                  <h4 className="font-medium text-windows-900 mb-3 flex items-center space-x-2">
                    <Key className="h-4 w-4 text-accent-600" />
                    <span>Primary Key</span>
                  </h4>
                  <div className="bg-accent-50 p-3 rounded-md">
                    <span className="font-mono text-accent-700">{tableData.primary_key}</span>
                  </div>
                </div>
              )}

              {/* Business Rules */}
              {tableData.business_rules && tableData.business_rules.length > 0 && (
                <div>
                  <h4 className="font-medium text-windows-900 mb-3 flex items-center space-x-2">
                    <AlertCircle className="h-4 w-4 text-warning-600" />
                    <span>Business Rules ({tableData.business_rules.length})</span>
                  </h4>
                  <div className="space-y-3">
                    {tableData.business_rules.map((rule: any, index: number) => (
                      <div key={index} className="p-4 bg-warning-50 border border-warning-200 rounded-md">
                        <div className="flex items-start justify-between mb-2">
                          <h5 className="font-medium text-warning-900">{rule.rule_name}</h5>
                          <span className="badge-windows badge-windows-warning text-xs">Rule {index + 1}</span>
                        </div>
                        <p className="text-warning-800 text-sm mb-2">{rule.description}</p>
                        <div className="space-y-1">
                          <div className="text-xs text-warning-700">
                            <span className="font-medium">Validation:</span> {rule.validation_logic}
                          </div>
                          <div className="text-xs text-warning-700">
                            <span className="font-medium">Error:</span> {rule.error_message}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Test Scenarios */}
              {tableData.test_scenarios && tableData.test_scenarios.length > 0 && (
                <div>
                  <h4 className="font-medium text-windows-900 mb-3 flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-accent-600" />
                    <span>Test Scenarios ({tableData.test_scenarios.length})</span>
                  </h4>
                  <div className="space-y-3">
                    {tableData.test_scenarios.map((scenario: any, index: number) => (
                      <div key={index} className="p-4 bg-accent-50 border border-accent-200 rounded-md">
                        <div className="flex items-start justify-between mb-2">
                          <h5 className="font-medium text-accent-900">{scenario.scenario_name}</h5>
                          <div className="flex items-center space-x-2">
                            <span className={`badge-windows badge-windows-${scenario.priority === 'HIGH' ? 'error' : 'warning'} text-xs`}>
                              {scenario.priority}
                            </span>
                            <span className="badge-windows badge-windows-info text-xs">#{index + 1}</span>
                          </div>
                        </div>
                        <p className="text-accent-800 text-sm mb-2">{scenario.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Data Generation Rules */}
              {tableData.data_generation_rules && tableData.data_generation_rules.length > 0 && (
                <div>
                  <h4 className="font-medium text-windows-900 mb-3 flex items-center space-x-2">
                    <Sparkles className="h-4 w-4 text-success-600" />
                    <span>Data Generation Rules ({tableData.data_generation_rules.length})</span>
                  </h4>
                  <div className="space-y-3">
                    {tableData.data_generation_rules.map((rule: any, index: number) => (
                      <div key={index} className="p-4 bg-success-50 border border-success-200 rounded-md">
                        <div className="flex items-start justify-between mb-2">
                          <h5 className="font-medium text-success-900">{rule.field_name}</h5>
                          <span className="badge-windows badge-windows-success text-xs">Rule {index + 1}</span>
                        </div>
                        <p className="text-success-800 text-sm mb-2">{rule.generation_logic}</p>
                        <div className="space-y-1">
                          <div className="text-xs text-success-700">
                            <span className="font-medium">Constraints:</span> {rule.constraints}
                          </div>
                          {rule.dependencies && rule.dependencies.length > 0 && (
                            <div className="text-xs text-success-700">
                              <span className="font-medium">Dependencies:</span> {rule.dependencies.join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderTestScenario = (scenario: any, index: number) => {
    const isExpanded = expandedScenarios.includes(scenario.id?.toString() || index.toString());
    const isSelected = selectedScenarios.includes(index);
    
    return (
      <div key={index} className="border border-windows-200 rounded-lg mb-3">
        <div className="p-4 bg-windows-50 border-b border-windows-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => toggleScenarioSelection(index)}
                className="h-4 w-4 text-accent-600 focus:ring-accent-500 border-windows-300 rounded"
              />
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-accent-600" />
                <span className="font-medium text-windows-900">{scenario.scenario_name}</span>
                <span className={`badge-windows badge-windows-${scenario.priority?.toLowerCase() || 'info'}`}>
                  {scenario.priority || 'MEDIUM'}
                </span>
                <span className="badge-windows badge-windows-info">
                  {scenario.scenario_type || 'positive'}
                </span>
              </div>
            </div>
            <button
              onClick={() => toggleScenarioExpansion(scenario.id?.toString() || index.toString())}
              className="p-1 hover:bg-windows-200 rounded transition-colors duration-200"
            >
              {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </button>
          </div>
        </div>
        
        {isExpanded && (
          <div className="p-4 bg-white">
            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-windows-900 mb-1">Description</h4>
                <p className="text-windows-600 text-sm">{scenario.description}</p>
              </div>
              <div>
                <h4 className="font-medium text-windows-900 mb-1">Test Conditions</h4>
                <p className="text-windows-600 text-sm">{scenario.test_conditions}</p>
              </div>
              <div>
                <h4 className="font-medium text-windows-900 mb-1">Data Requirements</h4>
                <p className="text-windows-600 text-sm">{scenario.data_requirements}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center relative">
        <div className="absolute top-0 right-0">
          <button
            onClick={() => setShowSettingsModal(true)}
            className="p-2 hover:bg-windows-100 rounded-lg transition-colors duration-200 group"
            title="Settings"
          >
            <Settings className="h-6 w-6 text-windows-600 group-hover:text-accent-600" />
          </button>
        </div>
        <h1 className="text-3xl font-bold text-windows-900">Add Test Scenarios To Your Data</h1>
        <p className="text-windows-600 mt-2 max-w-2xl mx-auto">
          AI has analyzed your data structure and identified patterns, relationships, and business rules.
        </p>
      </div>

      {/* Test Scenarios - Enhanced Prominent Section */}
      <div className="relative overflow-hidden rounded-xl border-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 shadow-xl">
        {/* Decorative background elements */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-100/20 to-purple-100/20"></div>
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-400/10 to-purple-400/10 rounded-full -translate-y-16 translate-x-16"></div>
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-indigo-400/10 to-blue-400/10 rounded-full translate-y-12 -translate-x-12"></div>
        
        <div className="relative p-10 border-b border-blue-200/50">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-4 mb-4">
                <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Test Scenarios
                  </h2>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                    <span className="text-blue-600 font-medium text-sm">AI-Powered Selection</span>
                  </div>
                </div>
              </div>
              <p className="text-gray-700 text-lg leading-relaxed max-w-2xl">
                Select from our comprehensive test library or create custom scenarios with AI to generate targeted test data for your specific use cases.
              </p>
            </div>
            <div className="flex items-center space-x-4 ml-8">
              <button
                onClick={() => {
                  console.log('Test Library button clicked');
                  setShowTestLibraryModal(true);
                }}
                className="group relative px-8 py-4 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 flex items-center space-x-3"
              >
                <div className="relative">
                  <Database className="h-5 w-5" />
                  <div className="absolute inset-0 bg-white/20 rounded-full blur-sm"></div>
                </div>
                <span>Choose from Test Library</span>
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
              </button>
              <button
                onClick={() => {
                  console.log('Create Scenario button clicked, current state:', showAddScenarios);
                  setShowAddScenarios(!showAddScenarios);
                }}
                className="group relative px-8 py-4 bg-white/80 backdrop-blur-sm border-2 border-blue-200 hover:border-blue-300 text-blue-700 hover:text-blue-800 font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 flex items-center space-x-3"
              >
                <div className="relative">
                  <Sparkles className="h-5 w-5" />
                  <div className="absolute inset-0 bg-blue-200/30 rounded-full blur-sm animate-pulse"></div>
                </div>
                <span>Create Test Scenario with AI</span>
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-100/50 to-transparent -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
              </button>
            </div>
          </div>
        </div>
        
        {/* Add Test Scenario Form - Always visible when active */}
        {showAddScenarios && (
          <div className="p-6 border-b border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 relative z-10">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-blue-800 mb-2">Describe your functional test scenario</label>
                <textarea
                  className="w-full p-4 border-2 border-blue-400 rounded-lg focus:border-blue-600 focus:ring-4 focus:ring-blue-200 focus:outline-none resize-none bg-white shadow-lg text-gray-900 font-medium"
                  value={userPrompt}
                  onChange={(e) => {
                    console.log('Textarea onChange triggered, value:', e.target.value);
                    setUserPrompt(e.target.value);
                  }}
                  onFocus={() => console.log('Textarea focused')}
                  onBlur={() => console.log('Textarea blurred')}
                  placeholder="e.g., Generate test data for users with high credit scores who have made recent transactions..."
                  rows={6}
                  style={{ 
                    minHeight: '150px',
                    zIndex: 1000,
                    position: 'relative'
                  }}
                  autoFocus={showAddScenarios}
                />
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleAddTestScenarios}
                  disabled={isLoading || !userPrompt.trim()}
                  className="btn-windows-primary flex items-center space-x-2"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                  <span>Create Scenario</span>
                </button>
                <button
                  onClick={() => {
                    setShowAddScenarios(false);
                    setUserPrompt('');
                  }}
                  className="btn-windows"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Selection Summary */}
        {selectedScenarios.length > 0 && (
          <div className="p-6 border-t border-blue-200 bg-gradient-to-r from-green-50 to-emerald-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-10 h-10 bg-green-100 rounded-full shadow-sm">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <span className="font-bold text-green-800 text-lg">
                    {selectedScenarios.length} scenario{selectedScenarios.length !== 1 ? 's' : ''} selected
                  </span>
                  <p className="text-green-600 text-sm">Ready to generate data with these scenarios</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedScenarios([])}
                className="px-4 py-2 bg-white border border-green-200 text-green-700 font-medium rounded-lg hover:bg-green-50 hover:border-green-300 transition-all duration-200 shadow-sm"
              >
                Clear Selection
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Schema Analysis Results */}
      {schemaAnalysis && (
        <div className="card-windows">
          <div className="p-6 border-b border-windows-200">
            <h2 className="text-xl font-semibold text-windows-900 flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-accent-600" />
              <span>AI Analysis Results</span>
            </h2>
            <p className="text-windows-600 mt-1">
              Click on any table to view detailed analysis including columns, relationships, and data patterns.
            </p>
          </div>
          <div className="p-6">
            {schemaAnalysis.tables && Array.isArray(schemaAnalysis.tables) ? (
              schemaAnalysis.tables.map((table: any) =>
                renderTableAnalysis(table.table_name, table)
              )
            ) : (
              <div className="text-center py-8">
                <Database className="h-12 w-12 text-windows-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-windows-900 mb-2">No tables found</h3>
                <p className="text-windows-600">Schema analysis did not return any table data.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Cross-Table Relationships */}
      {schemaAnalysis?.cross_table_relationships && schemaAnalysis.cross_table_relationships.length > 0 && (
        <div className="card-windows">
          <div className="p-6 border-b border-windows-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-windows-900 flex items-center space-x-2">
                  <Link className="h-5 w-5 text-accent-600" />
                  <span>Cross-Table Relationships</span>
                </h2>
                <p className="text-windows-600 mt-1">
                  AI has identified {schemaAnalysis.cross_table_relationships.length} relationships between tables and their business rules.
                </p>
              </div>
              <button
                onClick={() => setShowCrossTableRelationships(!showCrossTableRelationships)}
                className="btn-windows flex items-center space-x-2"
              >
                {showCrossTableRelationships ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
                <span>{showCrossTableRelationships ? 'Hide' : 'Show'} Relationships</span>
              </button>
            </div>
          </div>
          
          {showCrossTableRelationships && (
            <div className="p-6">
              <div className="space-y-4">
                {schemaAnalysis.cross_table_relationships.map((relationship: any, index: number) => (
                  <div key={index} className="p-4 bg-accent-50 border border-accent-200 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-medium text-accent-900">
                        {relationship.from_table} → {relationship.to_table}
                      </h3>
                      <span className="badge-windows badge-windows-accent text-xs">
                        {relationship.relationship_type}
                      </span>
                    </div>
                    <div className="space-y-2">
                      <div className="text-sm text-accent-800">
                        <span className="font-medium">Foreign Key:</span> {relationship.foreign_key}
                      </div>
                      {relationship.business_rules && relationship.business_rules.length > 0 && (
                        <div>
                          <div className="text-sm font-medium text-accent-800 mb-1">Business Rules:</div>
                          <ul className="list-disc list-inside text-sm text-accent-700 space-y-1">
                            {relationship.business_rules.map((rule: string, ruleIndex: number) => (
                              <li key={ruleIndex}>{rule}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}



      {/* Data Generation Loading Screen */}
      {showDataGenerationLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="mb-6">
                <Loader2 className="h-12 w-12 animate-spin text-accent-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-windows-900 mb-2">Generating Synthetic Data</h3>
                <p className="text-windows-600">Processing your test scenarios and generating data...</p>
              </div>
              
              <div className="space-y-3">
                {[
                  'Understanding your data',
                  'Understanding the schema',
                  'Applying relational logics',
                  'Applying test scenarios',
                  'Waiting for data generation to complete',
                  'Verifying generated files',
                  'Finalizing data preparation'
                ].map((step, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      index === dataGenerationStep 
                        ? 'bg-accent-600 text-white animate-pulse' 
                        : 'bg-windows-200 text-windows-600'
                    }`}>
                      <span className="text-xs font-medium">{index + 1}</span>
                    </div>
                    <span className={`text-sm ${
                      index === dataGenerationStep ? 'text-windows-900 font-medium' : 'text-windows-600'
                    }`}>
                      {step}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scenario Creation Loading Screen */}
      {showScenarioCreationLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="mb-6">
                <Loader2 className="h-12 w-12 animate-spin text-accent-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-windows-900 mb-2">Creating Test Scenario</h3>
                <p className="text-windows-600">AI is analyzing your input and generating scenarios...</p>
              </div>
              
              <div className="space-y-3">
                {[
                  'Analyzing user input',
                  'Evaluating tables for this criteria',
                  'Applying test scenarios'
                ].map((step, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      index === scenarioCreationStep 
                        ? 'bg-accent-600 text-white animate-pulse' 
                        : 'bg-windows-200 text-windows-600'
                    }`}>
                      <span className="text-xs font-medium">{index + 1}</span>
                    </div>
                    <span className={`text-sm ${
                      index === scenarioCreationStep ? 'text-windows-900 font-medium' : 'text-windows-600'
                    }`}>
                      {step}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Test Library Modal */}
      {console.log('Modal state:', showTestLibraryModal)}
      {showTestLibraryModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-windows-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold text-windows-900 flex items-center space-x-3">
                    <Database className="h-6 w-6 text-accent-600" />
                    <span>Test Scenario Library</span>
                  </h3>
                  <p className="text-windows-600 mt-1">
                    Select test scenarios from our comprehensive library to include in your data generation.
                  </p>
                </div>
                <button
                  onClick={() => setShowTestLibraryModal(false)}
                  className="btn-windows p-2"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="space-y-4">
                {testScenarios.length > 0 ? (
                  testScenarios.map((scenario, index) => (
                    <div key={index} className="p-4 border border-windows-200 rounded-lg hover:bg-windows-50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <input
                              type="checkbox"
                              checked={selectedScenarios.includes(scenario.id)}
                              onChange={() => toggleScenarioSelection(scenario.id)}
                              className="w-4 h-4 text-accent-600 border-windows-300 rounded focus:ring-accent-500"
                            />
                            <h4 className="font-semibold text-windows-900">{scenario.scenario_name}</h4>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${
                              scenario.priority === 'HIGH' ? 'bg-red-100 text-red-800' :
                              scenario.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {scenario.priority}
                            </span>
                          </div>
                          <p className="text-windows-600 mb-2">{scenario.description}</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="font-medium text-windows-700">Test Conditions:</span>
                              <p className="text-windows-600 mt-1">{scenario.test_conditions}</p>
                            </div>
                            <div>
                              <span className="font-medium text-windows-700">Data Requirements:</span>
                              <p className="text-windows-600 mt-1">{scenario.data_requirements}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-windows-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-windows-900 mb-2">No scenarios in library</h3>
                    <p className="text-windows-600">Create test scenarios with AI to populate the library.</p>
                  </div>
                )}
              </div>
            </div>
            
            <div className="p-6 border-t border-windows-200 bg-windows-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-success-600" />
                  <span className="font-medium text-success-900">
                    {selectedScenarios.length} scenario{selectedScenarios.length !== 1 ? 's' : ''} selected
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setSelectedScenarios([])}
                    className="btn-windows"
                  >
                    Clear Selection
                  </button>
                  <button
                    onClick={() => setShowTestLibraryModal(false)}
                    className="btn-windows-primary"
                  >
                    Apply Selection
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Check if this is a sample data run (runs 2 or 3) */}
      {(() => {
        const isSampleDataRun = state.currentRun?.run_id === '2' || state.currentRun?.run_id === '3';
        return (
          <div className="flex items-center justify-between mt-8 pt-6 pb-8 border-t border-windows-200 bg-white sticky bottom-0 z-10" style={{ bottom: '40px' }}>
            <button
              onClick={() => navigate('/data-source')}
              className="btn-windows flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back</span>
            </button>
            
            <button
              onClick={handleGenerateData}
              disabled={
                isGeneratingData || 
                !state.currentRun?.run_id
              }
              className="btn-windows-primary flex items-center space-x-2"
            >
              {isGeneratingData ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Generating Data...</span>
                </>
              ) : (
                <>
                  <span>Generate Synthetic Data</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>
        );
      })()}

      {/* Settings Modal */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-windows-900 flex items-center space-x-3">
                <Settings className="h-6 w-6 text-accent-600" />
                <span>Schema Analysis Settings</span>
              </h2>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="p-2 hover:bg-windows-100 rounded-lg transition-colors duration-200"
              >
                <X className="h-5 w-5 text-windows-600" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Column & Row Count Settings */}
              <div className="border border-windows-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-windows-900 mb-4 flex items-center space-x-2">
                  <Database className="h-5 w-5 text-accent-600" />
                  <span>Table Data Settings</span>
                </h3>
                
                {schemaAnalysis?.tables && schemaAnalysis.tables.map((table: any, index: number) => (
                  <div key={index} className="mb-4 p-4 bg-windows-50 rounded-lg border border-windows-200">
                    <h4 className="font-medium text-windows-900 mb-3">{table.table_name}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-windows-700 mb-1">
                          Row Count
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="100000"
                          placeholder="1000"
                          className="input-windows w-full"
                          defaultValue={1000}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-windows-700 mb-1">
                          Column Count
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="100"
                          placeholder="10"
                          className="input-windows w-full"
                          defaultValue={table.columns?.length || 5}
                          disabled
                        />
                      </div>
                    </div>
                    <div className="mt-3 text-xs text-windows-600">
                      Current columns: {table.columns?.length || 0}
                    </div>
                  </div>
                ))}
              </div>

              {/* Scenario Mix Settings */}
              <div className="border border-windows-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-windows-900 mb-4 flex items-center space-x-2">
                  <FileText className="h-5 w-5 text-accent-600" />
                  <span>Test Scenario Mix</span>
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">
                      Positive Scenarios (%)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      placeholder="60"
                      className="input-windows w-full"
                      defaultValue={60}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">
                      Negative Scenarios (%)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      placeholder="30"
                      className="input-windows w-full"
                      defaultValue={30}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">
                      Edge Cases (%)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      placeholder="10"
                      className="input-windows w-full"
                      defaultValue={10}
                    />
                  </div>
                </div>
                
                <div className="mt-4 p-3 bg-accent-50 rounded-lg border border-accent-200">
                  <div className="text-sm text-accent-800">
                    <div className="font-medium mb-2">Scenario Distribution:</div>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span>Positive (Valid Data):</span>
                        <span className="font-medium">60%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Negative (Invalid Data):</span>
                        <span className="font-medium">30%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Edge Cases (Boundary Testing):</span>
                        <span className="font-medium">10%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Data Quality Settings */}
              <div className="border border-windows-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-windows-900 mb-4 flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-accent-600" />
                  <span>Data Quality & Validation</span>
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-windows-900">Enable Data Validation</div>
                      <div className="text-sm text-windows-600">Validate generated data against business rules</div>
                    </div>
                    <input
                      type="checkbox"
                      defaultChecked
                      className="w-4 h-4 text-accent-600 border-windows-300 rounded focus:ring-accent-500"
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-windows-900">Cross-Table Relationship Validation</div>
                      <div className="text-sm text-windows-600">Ensure referential integrity between tables</div>
                    </div>
                    <input
                      type="checkbox"
                      defaultChecked
                      className="w-4 h-4 text-accent-600 border-windows-300 rounded focus:ring-accent-500"
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-windows-900">Data Anonymization</div>
                      <div className="text-sm text-windows-600">Mask sensitive data in generated datasets</div>
                    </div>
                    <input
                      type="checkbox"
                      className="w-4 h-4 text-accent-600 border-windows-300 rounded focus:ring-accent-500"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 mt-6 pt-4 border-t border-windows-200">
              <button
                onClick={() => setShowSettingsModal(false)}
                className="btn-windows"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  // TODO: Save settings logic
                  setShowSettingsModal(false);
                }}
                className="btn-windows-primary"
              >
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SchemaAnalysisPage;

export {}; 