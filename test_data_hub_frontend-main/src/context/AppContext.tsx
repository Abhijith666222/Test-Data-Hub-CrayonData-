import React, { createContext, useContext, useReducer, ReactNode } from 'react';

// Types
export interface Run {
  run_id: string;
  has_schema: boolean;
  has_synthetic_data: boolean;
  has_validation: boolean;
  has_input_data: boolean;
  created_at?: string;
}

export interface DataSource {
  id: string;
  name: string;
  type: 'sql' | 'oracle' | 'postgresql' | 'mysql' | 'mongodb' | 'redshift' | 'bigquery' | 'snowflake' | 'api' | 'file';
  connectionString?: string;
  host?: string;
  port?: string;
  database?: string;
  username?: string;
  password?: string;
  serviceName?: string;
  apiUrl?: string;
  apiKey?: string;
  filePath?: string;
  importQuery?: string;
  tables?: string[];
}

export interface ProductType {
  id: string;
  name: string;
  description: string;
  icon: string;
  available: boolean;
  features: string[];
}

export interface TestScenario {
  id: number;
  table_name: string;
  scenario_name: string;
  scenario_type: string;
  priority: string;
  description: string;
  test_conditions: string;
  data_requirements: string;
}

export interface AppState {
  runs: Run[];
  currentRun: Run | null;
  selectedProduct: ProductType | null;
  dataSources: DataSource[];
  selectedDataSources: DataSource[];
  testScenarios: TestScenario[];
  selectedTestScenarios: TestScenario[];
  schemaAnalysis: any;
  generatedData: any;
  isLoading: boolean;
  error: string | null;
  logs: LogMessage[];
  isDemoMode: boolean;
  loadedData: any;
  runConfig: any;
}

export interface LogMessage {
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
  message: string;
  run_id?: string;
  step?: string;
}

// Actions
type AppAction =
  | { type: 'SET_RUNS'; payload: Run[] }
  | { type: 'SET_CURRENT_RUN'; payload: Run | null }
  | { type: 'SET_SELECTED_PRODUCT'; payload: ProductType | null }
  | { type: 'SET_DATA_SOURCES'; payload: DataSource[] }
  | { type: 'SET_SELECTED_DATA_SOURCES'; payload: DataSource[] }
  | { type: 'SET_TEST_SCENARIOS'; payload: TestScenario[] }
  | { type: 'SET_SELECTED_TEST_SCENARIOS'; payload: TestScenario[] }
  | { type: 'SET_SCHEMA_ANALYSIS'; payload: any }
  | { type: 'SET_GENERATED_DATA'; payload: any }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_LOG'; payload: LogMessage }
  | { type: 'CLEAR_LOGS' }
  | { type: 'SET_DEMO_MODE'; payload: boolean }
  | { type: 'SET_LOADED_DATA'; payload: any }
  | { type: 'SET_RUN_CONFIG'; payload: any };

// Initial state
const initialState: AppState = {
  runs: [],
  currentRun: null,
  selectedProduct: null,
  dataSources: [],
  selectedDataSources: [],
  testScenarios: [],
  selectedTestScenarios: [],
  schemaAnalysis: null,
  generatedData: null,
  isLoading: false,
  error: null,
  logs: [],
  isDemoMode: false,
  loadedData: null,
  runConfig: null
};

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_RUNS':
      return { ...state, runs: action.payload };
    case 'SET_CURRENT_RUN':
      return { ...state, currentRun: action.payload };
    case 'SET_SELECTED_PRODUCT':
      return { ...state, selectedProduct: action.payload };
    case 'SET_DATA_SOURCES':
      return { ...state, dataSources: action.payload };
    case 'SET_SELECTED_DATA_SOURCES':
      return { ...state, selectedDataSources: action.payload };
    case 'SET_TEST_SCENARIOS':
      return { ...state, testScenarios: action.payload };
    case 'SET_SELECTED_TEST_SCENARIOS':
      return { ...state, selectedTestScenarios: action.payload };
    case 'SET_SCHEMA_ANALYSIS':
      return { ...state, schemaAnalysis: action.payload };
    case 'SET_GENERATED_DATA':
      return { ...state, generatedData: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'ADD_LOG':
      return { 
        ...state, 
        logs: [...state.logs, action.payload].slice(-100) // Keep last 100 logs
      };
    case 'CLEAR_LOGS':
      return { ...state, logs: [] };
    case 'SET_DEMO_MODE':
      return {
        ...state,
        isDemoMode: action.payload,
      };
    case 'SET_LOADED_DATA':
      return {
        ...state,
        loadedData: action.payload,
      };
    case 'SET_RUN_CONFIG':
      return {
        ...state,
        runConfig: action.payload,
      };
    default:
      return state;
  }
}

// Context
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider
interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

// Hook
export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
} 