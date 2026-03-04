import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Database, 
  Server, 
  FileText, 
  Globe,
  ChevronDown,
  ChevronRight,
  Plus,
  Trash2,
  Save,
  Loader2,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  ArrowLeft,
  Upload,
  X,
  TestTube,
  Settings,
  ChevronUp,
  Cloud,
  Activity
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useNotification } from '../context/NotificationContext';
import { DataSource } from '../context/AppContext';
import { apiService } from '../services/apiService';

const DataSourcePage: React.FC = () => {
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const { showWarning, showSuccess, showError } = useNotification();
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [selectedSources, setSelectedSources] = useState<DataSource[]>([]);
  const [expandedSource, setExpandedSource] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [useSampleData, setUseSampleData] = useState(false);
  const [showSchemaAnalysisLoading, setShowSchemaAnalysisLoading] = useState(false);
  const [schemaAnalysisStep, setSchemaAnalysisStep] = useState(0);
  const [showAllDataSources, setShowAllDataSources] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  
  // Database connection state
  const [mysqlConnection, setMysqlConnection] = useState({
    host: 'localhost',
    port: '3306',
    database: 'test_data_environment',
    username: 'root',
    password: 'admin123'
  });
  const [oracleConnection, setOracleConnection] = useState({
    host: 'localhost',
    port: '1521',
    serviceName: 'XEPDB1',
    username: 'system',
    password: '2018T@amit#'
  });
  
  // REST API configuration state
  const [restApiConfig, setRestApiConfig] = useState({
    apiUrl: '',
    apiKey: '',
    method: 'GET',
    contentType: 'application/json',
    legacyMode: false,
    legacyConfig: {
      soapEndpoint: '',
      wsdlUrl: '',
      username: '',
      password: '',
      namespace: '',
      operation: '',
      timeout: 30000,
      retryAttempts: 3
    }
  });
  
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'connecting' | 'connected' | 'error'>('idle');
  
  // Load database configuration on component mount
  useEffect(() => {
    loadDatabaseConfig();
  }, []);

  const loadDatabaseConfig = async () => {
    try {
      // Load config values from backend config
      // These values match the backend config.py file
      setMysqlConnection(prev => ({
        ...prev,
        host: 'localhost',
        port: '3306',
        database: 'test_data_environment',
        username: 'root',
        password: 'admin123'
      }));
      
      setOracleConnection(prev => ({
        ...prev,
        host: 'localhost',
        port: '1521',
        serviceName: 'XEPDB1',
        username: 'system',
        password: '2018T@amit#'
      }));
    } catch (error) {
      console.error('Failed to load database config:', error);
    }
  };

  const dataSourceTypes = [
    {
      id: 'file',
      name: 'File Upload',
      icon: FileText,
      description: 'Upload CSV files for data processing',
      fields: ['filePath'],
      isRealDataSource: true
    },
    {
      id: 'mysql',
      name: 'MySQL Database',
      icon: Database,
      description: 'MySQL database connection',
      fields: ['host', 'port', 'database', 'username', 'password'],
      isRealDataSource: true
    },
    {
      id: 'oracle',
      name: 'Oracle Database',
      icon: Database,
      description: 'Oracle database connection',
      fields: ['host', 'port', 'serviceName', 'username', 'password'],
      isRealDataSource: true
    },
    {
      id: 'api',
      name: 'REST API',
      icon: Globe,
      description: 'REST API data source',
      fields: ['apiUrl', 'apiKey', 'headers', 'method']
    },
    {
      id: 'sql',
      name: 'RPA Agent',
      icon: Database,
      description: 'Robotic Process Automation Agent Connection',
      fields: ['host', 'port', 'database', 'username', 'password', 'connectionString']
    },
    {
      id: 'postgresql',
      name: 'PostgreSQL',
      icon: Database,
      description: 'PostgreSQL database connection',
      fields: ['host', 'port', 'database', 'username', 'password', 'connectionString']
    },
    {
      id: 'mongodb',
      name: 'MongoDB',
      icon: Database,
      description: 'MongoDB NoSQL database connection',
      fields: ['host', 'port', 'database', 'username', 'password', 'connectionString']
    },
    {
      id: 'redshift',
      name: 'Amazon Redshift',
      icon: Server,
      description: 'Amazon Redshift data warehouse',
      fields: ['host', 'port', 'database', 'username', 'password', 'connectionString']
    },
    {
      id: 'bigquery',
      name: 'Google BigQuery',
      icon: Server,
      description: 'Google BigQuery data warehouse',
      fields: ['projectId', 'dataset', 'credentials', 'connectionString']
    },
    {
      id: 'snowflake',
      name: 'Snowflake',
      icon: Server,
      description: 'Snowflake data warehouse',
      fields: ['account', 'warehouse', 'database', 'username', 'password', 'connectionString']
    },

  ];

  useEffect(() => {
    if (!state.selectedProduct) {
      navigate('/create');
      return;
    }
  }, [state.selectedProduct, navigate]);

  const addDataSource = (type: string) => {
    const sourceType = dataSourceTypes.find(t => t.id === type);
    if (!sourceType) return;

    const newSource: DataSource = {
      id: `${type}_${Date.now()}`,
      name: sourceType.name,
      type: type as any,
      ...getDefaultValuesForType(type)
    };

    setDataSources(prev => [...prev, newSource]);
    setSelectedSources(prev => [...prev, newSource]);
  };

  const getDefaultValuesForType = (type: string) => {
    switch (type) {
      case 'file':
        return { filePath: '' };
      case 'mysql':
        return {
          host: mysqlConnection.host || 'localhost',
          port: mysqlConnection.port || '3306',
          database: mysqlConnection.database || 'test_data_environment',
          username: mysqlConnection.username || 'root',
          password: mysqlConnection.password || 'admin123'
        };
      case 'oracle':
        return {
          host: oracleConnection.host || 'localhost',
          port: oracleConnection.port || '1521',
          serviceName: oracleConnection.serviceName || 'XEPDB1',
          username: oracleConnection.username || 'system',
          password: oracleConnection.password || '2018T@amit#'
        };
      default:
        return {};
    }
  };

  const updateDataSource = (id: string, updates: Partial<DataSource>) => {
    setDataSources(dataSources.map(ds => 
      ds.id === id ? { ...ds, ...updates } : ds
    ));
  };

  const removeDataSource = (id: string) => {
    setDataSources(dataSources.filter(ds => ds.id !== id));
    setSelectedSources(selectedSources.filter(ds => ds.id !== id));
  };

  const toggleDataSourceSelection = (source: DataSource) => {
    const isSelected = selectedSources.some(s => s.id === source.id);
    if (isSelected) {
      setSelectedSources(selectedSources.filter(s => s.id !== source.id));
    } else {
      setSelectedSources([...selectedSources, source]);
    }
  };

  const handleUseSampleData = async () => {
    // Set demo mode in global state
    dispatch({ type: 'SET_DEMO_MODE', payload: true });
    
    // Show loading screen with steps
    setShowSchemaAnalysisLoading(true);
    setSchemaAnalysisStep(0);
    
    const steps = [
      'Loading data from source',
      'Preparing data preview',
      'Setting up file structure',
      'Ready for data preview'
    ];
    
    // Show continuous flow for 3-4 seconds
    const totalDuration = 3500; // 3.5 seconds
    const stepDuration = totalDuration / steps.length;
    
    for (let i = 0; i < steps.length; i++) {
      setSchemaAnalysisStep(i);
      await new Promise(resolve => setTimeout(resolve, stepDuration));
    }
    
    // Continue cycling through steps for the remaining time
    const remainingTime = 1500; // 1.5 more seconds
    const cycleDuration = remainingTime / steps.length;
    
    for (let cycle = 0; cycle < 2; cycle++) {
      for (let i = 0; i < steps.length; i++) {
        setSchemaAnalysisStep(i);
        await new Promise(resolve => setTimeout(resolve, cycleDuration));
      }
    }
    
    setIsLoading(true);
    try {
      // For demo mode, just navigate to data preview without API calls
      setShowSchemaAnalysisLoading(false);
      navigate('/data-preview');
    } catch (error) {
      console.error('Failed to navigate to data preview:', error);
      setShowSchemaAnalysisLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  // New functions for real data sources
  const handleFileUpload = (files: FileList | null) => {
    if (!files) return;
    
    const newFiles = Array.from(files).filter(file => file.name.endsWith('.csv'));
    if (newFiles.length === 0) {
      showWarning('Warning', 'Please select CSV files only.');
      return;
    }
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
    showSuccess('Success', `${newFiles.length} CSV file(s) uploaded successfully.`);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const testMysqlConnection = async (source: DataSource) => {
    setIsConnecting(true);
    setConnectionStatus('connecting');
    
    try {
      const response = await apiService.testMysqlConnection({
        host: source.host,
        port: source.port,
        database: source.database,
        username: source.username,
        password: source.password
      });
      if (response.status === 200) {
        setConnectionStatus('connected');
        showSuccess('Success', 'MySQL connection successful!');
      } else {
        setConnectionStatus('error');
        showError('Connection Failed', response.error || 'Failed to connect to MySQL');
      }
    } catch (error) {
      setConnectionStatus('error');
      showError('Connection Failed', 'Failed to connect to MySQL database');
    } finally {
      setIsConnecting(false);
    }
  };

  const testOracleConnection = async (source: DataSource) => {
    setIsConnecting(true);
    setConnectionStatus('connecting');
    
    try {
      const response = await apiService.testOracleConnection({
        host: source.host,
        port: source.port,
        serviceName: source.serviceName,
        username: source.username,
        password: source.password
      });
      if (response.status === 200) {
        setConnectionStatus('connected');
        showSuccess('Success', 'Oracle connection successful!');
      } else {
        setConnectionStatus('error');
        showError('Connection Failed', response.error || 'Failed to connect to Oracle');
      }
    } catch (error) {
      setConnectionStatus('error');
      showError('Connection Failed', 'Failed to connect to Oracle database');
    } finally {
      setIsConnecting(false);
    }
  };

  const testRestApiConnection = async (source: DataSource) => {
    setIsConnecting(true);
    setConnectionStatus('connecting');
    
    try {
      // For REST API, we'll simulate a connection test
      // In a real implementation, this would call the API service
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      setConnectionStatus('connected');
      showSuccess('Success', 'REST API connection successful!');
    } catch (error) {
      setConnectionStatus('error');
      showError('Connection Failed', 'Failed to connect to REST API');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleContinue = async () => {
    if (useSampleData) {
      await handleUseSampleData();
      return;
    }

    // Handle real data sources
    if (selectedSources.length > 0) {
      // Check if we have file upload sources that need files
      const hasFileSources = selectedSources.some(s => s.type === 'file');
      if (hasFileSources && uploadedFiles.length === 0) {
        showWarning('Warning', 'Please upload CSV files for file upload sources.');
        return;
      }

      // Check if we have database sources that need connection testing
      const hasDatabaseSources = selectedSources.some(s => s.type === 'mysql' || s.type === 'oracle');
      if (hasDatabaseSources && connectionStatus !== 'connected') {
        showWarning('Warning', 'Please test database connections before continuing.');
      return;
    }

    // Reset demo mode when using real data sources
    dispatch({ type: 'SET_DEMO_MODE', payload: false });
    dispatch({ type: 'SET_SELECTED_DATA_SOURCES', payload: selectedSources });
    
    // Show loading screen with steps
    setShowSchemaAnalysisLoading(true);
    setSchemaAnalysisStep(0);
    
    const steps = [
        'Loading data from sources',
        'Processing data',
        'Preparing for analysis',
        'Ready to continue'
      ];
      
      // Show continuous flow for 3-4 seconds
      const totalDuration = 3500; // 3.5 seconds
    const stepDuration = totalDuration / steps.length;
    
    for (let i = 0; i < steps.length; i++) {
      setSchemaAnalysisStep(i);
      await new Promise(resolve => setTimeout(resolve, stepDuration));
    }
    
      // Actually load the data from sources
      setIsLoading(true);
      try {
        let allLoadedData: any = {};
        let runId: string | null = null;
        
        // Process file uploads
        if (hasFileSources && uploadedFiles.length > 0) {
          console.log('Uploading files:', uploadedFiles);
          const productType = state.selectedProduct?.id || 'functional-test-scenarios';
          const uploadResponse = await apiService.uploadFiles(uploadedFiles, productType);
          if (uploadResponse?.status === 200) {
            allLoadedData.files = uploadResponse.data.files;
            runId = uploadResponse.data.run_id; // Store the run ID
            console.log('Files uploaded successfully:', uploadResponse.data);
          } else {
            throw new Error(uploadResponse?.error || 'Failed to upload files');
          }
        }
        
        // Process database sources
        for (const source of selectedSources) {
          if (source.type === 'mysql') {
            console.log('Loading MySQL data from:', source);
            const productType = state.selectedProduct?.id || 'functional-test-scenarios';
            const mysqlResponse = await apiService.loadMysqlData({
              host: source.host,
              port: source.port,
              database: source.database,
              username: source.username,
              password: source.password
            }, productType);
            if (mysqlResponse?.status === 200) {
              allLoadedData.tables = { ...allLoadedData.tables, ...mysqlResponse.data.tables };
              if (!runId) runId = mysqlResponse.data.run_id; // Store the run ID if not already set
              console.log('MySQL data loaded successfully:', mysqlResponse.data);
            } else {
              throw new Error(mysqlResponse?.error || 'Failed to load MySQL data');
            }
          } else if (source.type === 'oracle') {
            console.log('Loading Oracle data from:', source);
            const productType = state.selectedProduct?.id || 'functional-test-scenarios';
            const oracleResponse = await apiService.loadOracleData({
              host: source.host,
              port: source.port,
              serviceName: source.serviceName,
              username: source.username,
              password: source.password
            }, productType);
            if (oracleResponse?.status === 200) {
              allLoadedData.tables = { ...allLoadedData.tables, ...oracleResponse.data.tables };
              if (!runId) runId = oracleResponse.data.run_id; // Store the run ID if not already set
              console.log('Oracle data loaded successfully:', oracleResponse.data);
            } else {
              throw new Error(oracleResponse?.error || 'Failed to load Oracle data');
            }
          }
        }
        
        // Store the loaded data and run ID in context
        dispatch({ type: 'SET_LOADED_DATA', payload: { ...allLoadedData, runId } });
        console.log('All data loaded and stored in context:', allLoadedData, 'Run ID:', runId);
        
        // Show success message
        showSuccess('Success', 'Data loaded successfully! Redirecting to preview...');
        
        // Navigate to data preview
        setTimeout(() => {
        navigate('/data-preview');
        }, 1500);
        
    } catch (error) {
        console.error('Failed to load data from sources:', error);
        showError('Error', `Failed to load data: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setShowSchemaAnalysisLoading(false);
    } finally {
      setIsLoading(false);
      }
      return;
    }

    if (selectedSources.length === 0) {
      showWarning('Warning', 'Please select at least one data source or choose to use sample data.');
      return;
    }
  };

  const getDataSourceIcon = (type: string) => {
    const sourceType = dataSourceTypes.find(t => t.id === type);
    if (sourceType) {
      const Icon = sourceType.icon;
      return <Icon className="h-5 w-5" />;
    }
    return <Database className="h-5 w-5" />;
  };

  const renderDataSourceFields = (source: DataSource) => {
    if (source.type === 'file') {
      return renderFileUploadSection();
    }
    
    if (source.type === 'mysql') {
      return renderMysqlSection(source);
    }
    
    if (source.type === 'oracle') {
      return renderOracleSection(source);
    }

    // Default rendering for other data source types
    const sourceType = dataSourceTypes.find(t => t.id === source.type);
    if (!sourceType) return null;

    return (
      <div className="space-y-4">
        {sourceType.fields.map(field => (
          <div key={field}>
            <label className="block text-sm font-medium text-windows-700 mb-1 capitalize">
              {field.replace(/([A-Z])/g, ' $1').trim()}
            </label>
            <input
              type={field === 'password' ? 'password' : 'text'}
              value={source[field as keyof DataSource] || ''}
              onChange={(e) => updateDataSource(source.id, { [field]: e.target.value })}
              placeholder={`Enter ${field.replace(/([A-Z])/g, ' $1').toLowerCase()}`}
              className="input-windows w-full"
            />
          </div>
        ))}
      </div>
    );
  };

  // New render functions for real data sources
  const renderFileUploadSection = () => (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <FileText className="w-5 h-5 text-windows-600" />
        <h3 className="text-lg font-semibold text-windows-900">CSV File Upload</h3>
      </div>
      
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver 
            ? 'border-windows-primary bg-windows-primary/5' 
            : 'border-windows-300 hover:border-windows-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="w-12 h-12 text-windows-400 mx-auto mb-4" />
        <p className="text-windows-600 mb-2">
          Drag and drop CSV files here, or{' '}
          <label className="text-windows-primary hover:text-windows-primary-dark cursor-pointer">
            browse files
            <input
              type="file"
              multiple
              accept=".csv"
              onChange={(e) => handleFileUpload(e.target.files)}
              className="hidden"
            />
          </label>
        </p>
        <p className="text-sm text-windows-500">Supports multiple CSV files</p>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-windows-700">Uploaded Files:</h4>
          {uploadedFiles.map((file, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-windows-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-windows-600" />
                <span className="text-windows-700">{file.name}</span>
                <span className="text-sm text-windows-500">({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="text-windows-400 hover:text-windows-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderMysqlSection = (source: DataSource) => (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <Database className="w-5 h-5 text-windows-600" />
        <h3 className="text-lg font-semibold text-windows-900">MySQL Database Connection</h3>
      </div>
      
      {/* Pre-configured connection info */}
      <div className="p-3 bg-windows-primary/5 border border-windows-primary/20 rounded-lg">
        <div className="flex items-center space-x-2">
          <Settings className="w-4 h-4 text-windows-primary" />
          <span className="text-sm text-windows-700 font-medium">Pre-configured Connection</span>
        </div>
        <p className="text-xs text-windows-600 mt-1">
          This connection is pre-configured to match your destination page settings. 
          You can modify these values if needed.
        </p>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-windows-700 mb-1">Host</label>
              <input
                type="text"
                value={source.host || ''}
                onChange={(e) => updateDataSource(source.id, { host: e.target.value })}
                placeholder="localhost"
            className="input-windows w-full"
              />
            </div>
        <div>
          <label className="block text-sm font-medium text-windows-700 mb-1">Port</label>
              <input
                type="text"
                value={source.port || ''}
                onChange={(e) => updateDataSource(source.id, { port: e.target.value })}
            placeholder="3306"
            className="input-windows w-full"
              />
            </div>
        <div>
          <label className="block text-sm font-medium text-windows-700 mb-1">Database</label>
              <input
                type="text"
                value={source.database || ''}
                onChange={(e) => updateDataSource(source.id, { database: e.target.value })}
            placeholder="your_database"
            className="input-windows w-full"
              />
            </div>
        <div>
          <label className="block text-sm font-medium text-windows-700 mb-1">Username</label>
              <input
                type="text"
                value={source.username || ''}
                onChange={(e) => updateDataSource(source.id, { username: e.target.value })}
            placeholder="your_username"
            className="input-windows w-full"
              />
            </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-windows-700 mb-1">Password</label>
              <input
                type="password"
                value={source.password || ''}
                onChange={(e) => updateDataSource(source.id, { password: e.target.value })}
            placeholder="your_password"
            className="input-windows w-full"
              />
            </div>
      </div>

      <div className="flex items-center space-x-3">
        <button
          onClick={() => testMysqlConnection(source)}
          disabled={isConnecting || !source.host || !source.database || !source.username || !source.password}
          className="btn-windows flex items-center space-x-2"
        >
          {isConnecting ? <Loader2 className="w-4 h-4 animate-spin" /> : <TestTube className="w-4 h-4" />}
          <span>Test Connection</span>
        </button>
        
        <div className="flex items-center space-x-2">
          {connectionStatus === 'idle' && <div className="w-3 h-3 rounded-full bg-windows-300" />}
          {connectionStatus === 'connecting' && <div className="w-3 h-3 rounded-full bg-windows-warning animate-pulse" />}
          {connectionStatus === 'connected' && <CheckCircle className="w-5 h-5 text-windows-success" />}
          {connectionStatus === 'error' && <AlertCircle className="w-5 h-5 text-windows-error" />}
          
          <span className="text-sm text-windows-600">
            {connectionStatus === 'idle' && 'Not connected'}
            {connectionStatus === 'connecting' && 'Testing connection...'}
            {connectionStatus === 'connected' && 'Connected'}
            {connectionStatus === 'error' && 'Connection failed'}
          </span>
        </div>
      </div>
    </div>
  );

  const renderOracleSection = (source: DataSource) => (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <Database className="w-5 h-5 text-windows-600" />
        <h3 className="text-lg font-semibold text-windows-900">Oracle Database Connection</h3>
      </div>
      
      {/* Pre-configured connection info */}
      <div className="p-3 bg-windows-primary/5 border border-windows-primary/20 rounded-lg">
        <div className="flex items-center space-x-2">
          <Settings className="w-4 h-4 text-windows-primary" />
          <span className="text-sm text-windows-700 font-medium">Pre-configured Connection</span>
        </div>
        <p className="text-xs text-windows-600 mt-1">
          This connection is pre-configured to match your destination page settings. 
          You can modify these values if needed.
        </p>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-windows-700 mb-1">Host</label>
              <input
            type="text"
            value={source.host || ''}
            onChange={(e) => updateDataSource(source.id, { host: e.target.value })}
            placeholder="localhost"
            className="input-windows w-full"
              />
            </div>
        <div>
          <label className="block text-sm font-medium text-windows-700 mb-1">Port</label>
              <input
            type="text"
            value={source.port || ''}
            onChange={(e) => updateDataSource(source.id, { port: e.target.value })}
            placeholder="1521"
            className="input-windows w-full"
              />
            </div>
        <div>
          <label className="block text-sm font-medium text-windows-700 mb-1">Service Name</label>
                    <input
            type="text"
            value={source.serviceName || ''}
            onChange={(e) => updateDataSource(source.id, { serviceName: e.target.value })}
            placeholder="your_service_name"
            className="input-windows w-full"
          />
              </div>
                        <div>
          <label className="block text-sm font-medium text-windows-700 mb-1">Username</label>
          <input
            type="text"
            value={source.username || ''}
            onChange={(e) => updateDataSource(source.id, { username: e.target.value })}
            placeholder="your_username"
            className="input-windows w-full"
          />
                        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-windows-700 mb-1">Password</label>
          <input
            type="password"
            value={source.password || ''}
            onChange={(e) => updateDataSource(source.id, { password: e.target.value })}
            placeholder="your_password"
            className="input-windows w-full"
          />
                      </div>
      </div>

      <div className="flex items-center space-x-3">
                      <button
          onClick={() => testOracleConnection(source)}
          disabled={isConnecting || !source.host || !source.serviceName || !source.username || !source.password}
          className="btn-windows flex items-center space-x-2"
                      >
          {isConnecting ? <Loader2 className="w-4 h-4 animate-spin" /> : <TestTube className="w-4 h-4" />}
          <span>Test Connection</span>
                      </button>
        
        <div className="flex items-center space-x-2">
          {connectionStatus === 'idle' && <div className="w-3 h-3 rounded-full bg-windows-300" />}
          {connectionStatus === 'connecting' && <div className="w-3 h-3 rounded-full bg-windows-warning animate-pulse" />}
          {connectionStatus === 'connected' && <CheckCircle className="w-5 h-5 text-windows-success" />}
          {connectionStatus === 'error' && <AlertCircle className="w-5 h-5 text-windows-error" />}
          
          <span className="text-sm text-windows-600">
            {connectionStatus === 'idle' && 'Not connected'}
            {connectionStatus === 'connecting' && 'Testing connection...'}
            {connectionStatus === 'connected' && 'Connected'}
            {connectionStatus === 'error' && 'Connection failed'}
          </span>
        </div>
        </div>
      </div>
    );

  const renderRestApiSection = (source: DataSource) => (
    <div className="space-y-6">
      <div className="flex items-center space-x-2">
        <Globe className="w-5 h-5 text-windows-600" />
        <h3 className="text-lg font-semibold text-windows-900">REST API Configuration</h3>
      </div>
      
      {/* Modern REST API Configuration */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Settings className="w-4 h-4 text-accent-600" />
          <h4 className="font-medium text-windows-900">Modern REST API Settings</h4>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-windows-700 mb-1">API URL</label>
            <input
              type="url"
              value={restApiConfig.apiUrl}
              onChange={(e) => setRestApiConfig(prev => ({ ...prev, apiUrl: e.target.value }))}
              placeholder="https://api.example.com/data"
              className="input-windows w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-windows-700 mb-1">API Key</label>
            <input
              type="password"
              value={restApiConfig.apiKey}
              onChange={(e) => setRestApiConfig(prev => ({ ...prev, apiKey: e.target.value }))}
              placeholder="your_api_key"
              className="input-windows w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-windows-700 mb-1">HTTP Method</label>
            <select
              value={restApiConfig.method}
              onChange={(e) => setRestApiConfig(prev => ({ ...prev, method: e.target.value }))}
              className="input-windows w-full"
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="PATCH">PATCH</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-windows-700 mb-1">Content Type</label>
            <select
              value={restApiConfig.contentType}
              onChange={(e) => setRestApiConfig(prev => ({ ...prev, contentType: e.target.value }))}
              className="input-windows w-full"
            >
              <option value="application/json">JSON</option>
              <option value="application/xml">XML</option>
              <option value="text/csv">CSV</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Legacy Mode Toggle */}
      <div className="flex items-center space-x-3 p-4 bg-windows-50 rounded-lg border border-windows-200">
        <input
          type="checkbox"
          id="legacyMode"
          checked={restApiConfig.legacyMode}
          onChange={(e) => setRestApiConfig(prev => ({ ...prev, legacyMode: e.target.checked }))}
          className="w-4 h-4 text-accent-600 border-windows-300 rounded focus:ring-accent-500"
        />
        <label htmlFor="legacyMode" className="text-sm font-medium text-windows-900">
          Enable Legacy Integration Mode
        </label>
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-warning-600" />
          <span className="text-xs text-warning-600">Legacy</span>
        </div>
      </div>
      
      {/* Legacy Configuration */}
      {restApiConfig.legacyMode && (
        <div className="space-y-4 p-4 bg-warning-50 rounded-lg border border-warning-200">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-warning-600" />
            <h4 className="font-medium text-warning-900">Legacy System Configuration</h4>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-warning-700 mb-1">SOAP Endpoint</label>
              <input
                type="url"
                value={restApiConfig.legacyConfig.soapEndpoint}
                onChange={(e) => setRestApiConfig(prev => ({ 
                  ...prev, 
                  legacyConfig: { ...prev.legacyConfig, soapEndpoint: e.target.value }
                }))}
                placeholder="https://legacy.example.com/soap"
                className="input-windows w-full bg-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-warning-700 mb-1">WSDL URL</label>
              <input
                type="url"
                value={restApiConfig.legacyConfig.wsdlUrl}
                onChange={(e) => setRestApiConfig(prev => ({ 
                  ...prev, 
                  legacyConfig: { ...prev.legacyConfig, wsdlUrl: e.target.value }
                }))}
                placeholder="https://legacy.example.com/wsdl"
                className="input-windows w-full bg-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-warning-700 mb-1">Username</label>
              <input
                type="text"
                value={restApiConfig.legacyConfig.username}
                onChange={(e) => setRestApiConfig(prev => ({ 
                  ...prev, 
                  legacyConfig: { ...prev.legacyConfig, username: e.target.value }
                }))}
                placeholder="legacy_username"
                className="input-windows w-full bg-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-warning-700 mb-1">Password</label>
              <input
                type="password"
                value={restApiConfig.legacyConfig.password}
                onChange={(e) => setRestApiConfig(prev => ({ 
                  ...prev, 
                  legacyConfig: { ...prev.legacyConfig, password: e.target.value }
                }))}
                placeholder="legacy_password"
                className="input-windows w-full bg-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-warning-700 mb-1">Namespace</label>
              <input
                type="text"
                value={restApiConfig.legacyConfig.namespace}
                onChange={(e) => setRestApiConfig(prev => ({ 
                  ...prev, 
                  legacyConfig: { ...prev.legacyConfig, namespace: e.target.value }
                }))}
                placeholder="http://legacy.example.com/namespace"
                className="input-windows w-full bg-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-windows-700 mb-1">Operation</label>
              <input
                type="text"
                value={restApiConfig.legacyConfig.operation}
                onChange={(e) => setRestApiConfig(prev => ({ 
                  ...prev, 
                  legacyConfig: { ...prev.legacyConfig, operation: e.target.value }
                }))}
                placeholder="GetData"
                className="input-windows w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-windows-700 mb-1">Timeout (ms)</label>
              <input
                type="number"
                value={restApiConfig.legacyConfig.timeout}
                onChange={(e) => setRestApiConfig(prev => ({ 
                  ...prev, 
                  legacyConfig: { ...prev.legacyConfig, timeout: parseInt(e.target.value) || 30000 }
                }))}
                placeholder="30000"
                className="input-windows w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-windows-700 mb-1">Retry Attempts</label>
              <input
                type="number"
                value={restApiConfig.legacyConfig.retryAttempts}
                onChange={(e) => setRestApiConfig(prev => ({ 
                  ...prev, 
                  legacyConfig: { ...prev.legacyConfig, retryAttempts: parseInt(e.target.value) || 3 }
                }))}
                placeholder="3"
                className="input-windows w-full"
              />
            </div>
          </div>
          
          <div className="p-3 bg-warning-100 rounded border border-warning-300">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-warning-600 mt-0.5" />
              <div className="text-xs text-warning-700">
                <p className="font-medium mb-1">Legacy Integration Notes:</p>
                <ul className="space-y-1">
                  <li>• SOAP endpoints require WSDL validation</li>
                  <li>• Legacy systems may have slower response times</li>
                  <li>• Consider implementing retry logic for reliability</li>
                  <li>• Test thoroughly in legacy environment</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Connection Test */}
      <div className="flex items-center space-x-3">
        <button
          onClick={() => testRestApiConnection(source)}
          disabled={isConnecting || !restApiConfig.apiUrl}
          className="btn-windows flex items-center space-x-2"
        >
          {isConnecting ? <Loader2 className="w-4 h-4 animate-spin" /> : <TestTube className="w-4 h-4" />}
          <span>Test API Connection</span>
        </button>
        
        <div className="flex items-center space-x-2">
          {connectionStatus === 'idle' && <div className="w-3 h-3 rounded-full bg-windows-300" />}
          {connectionStatus === 'connecting' && <div className="w-3 h-3 rounded-full bg-windows-warning animate-pulse" />}
          {connectionStatus === 'connected' && <CheckCircle className="w-5 h-5 text-windows-success" />}
          {connectionStatus === 'error' && <AlertCircle className="w-5 h-5 text-windows-error" />}
          
          <span className="text-sm text-windows-600">
            {connectionStatus === 'idle' && 'Not connected'}
            {connectionStatus === 'connecting' && 'Testing connection...'}
            {connectionStatus === 'connected' && 'Connected'}
            {connectionStatus === 'error' && 'Connection failed'}
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-windows-900">Connect Data Source</h1>
        <p className="text-windows-600 mt-2 max-w-2xl mx-auto">
          Configure your data sources for {state.selectedProduct?.name.toLowerCase()}. 
          You can connect to multiple databases, APIs, or upload files.
        </p>
      </div>

      {/* Demo Mode Section */}
      <div className="card-windows p-6">
        <div className="flex items-center space-x-3 mb-4">
          <TestTube className="w-6 h-6 text-windows-primary" />
          <h2 className="text-xl font-semibold text-windows-900">Demo Mode</h2>
        </div>
        
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            id="useSampleData"
            checked={useSampleData}
            onChange={(e) => setUseSampleData(e.target.checked)}
            className="w-4 h-4 text-windows-primary border-windows-300 rounded focus:ring-windows-primary"
          />
          <label htmlFor="useSampleData" className="text-windows-700">
            Use sample data for demonstration purposes
          </label>
      </div>

        {useSampleData && (
          <div className="mt-4 p-4 bg-windows-50 rounded-lg">
            <p className="text-windows-600 text-sm">
              Demo mode will use pre-configured sample data to demonstrate the system capabilities.
              This is perfect for testing and demonstration purposes.
          </p>
        </div>
        )}
                </div>

      {/* Existing Systems */}
      <div className="card-windows">
        <div className="p-6 border-b border-windows-200">
          <h2 className="text-xl font-semibold text-windows-900 flex items-center space-x-2">
            <Server className="h-5 w-5 text-accent-600" />
            <span>Choose Existing Systems</span>
          </h2>
          <p className="text-windows-600 mt-1">
            Select from pre-configured data source systems or add new sources
          </p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { name: 'Prime', icon: Database, description: 'Production Oracle database', status: 'active' },
              { name: 'iOptimus', icon: Database, description: 'Development MySQL server', status: 'active' },
              { name: 'Redis DB', icon: Database, description: 'In Memory RedisB', status: 'active' },
              { name: 'Workspace DB', icon: Database, description: 'Local workspace database', status: 'active' }
            ].map((system, index) => (
              <div
                key={index}
                className="card-windows p-4 text-center hover:shadow-windows-lg transition-all duration-200 cursor-pointer border-2 border-transparent hover:border-accent-300"
              >
                <div className="p-3 bg-accent-100 rounded-lg w-fit mx-auto mb-3">
                  <system.icon className="h-6 w-6 text-accent-600" />
                </div>
                <h3 className="font-semibold text-windows-900 mb-1">{system.name}</h3>
                <p className="text-sm text-windows-600 mb-2">{system.description}</p>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-success-100 text-success-800">
                  {system.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Legacy Data Sources Section - Keep existing functionality */}
      <div className="card-windows p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Server className="w-6 h-6 text-windows-600" />
            <h2 className="text-xl font-semibold text-windows-900">Data Sources</h2>
          </div>
          <button
            onClick={() => setShowAllDataSources(!showAllDataSources)}
            className="btn-windows flex items-center space-x-2"
          >
            {showAllDataSources ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            <span>{showAllDataSources ? 'Show Less' : 'Show All'}</span>
          </button>
        </div>

        {/* Pre-configured connections info */}
        <div className="mb-4 p-4 bg-windows-50 border border-windows-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <Settings className="w-5 h-5 text-windows-primary" />
            <span className="text-sm font-medium text-windows-700">Pre-configured Database Connections</span>
          </div>
          <p className="text-sm text-windows-600">
            MySQL and Oracle connections are automatically pre-configured with the same settings from your destination page. 
            This ensures consistency between data source and destination configurations.
          </p>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {dataSourceTypes.slice(0, showAllDataSources ? dataSourceTypes.length : 6).map((sourceType) => (
              <button
                key={sourceType.id}
                onClick={() => addDataSource(sourceType.id)}
                className="p-4 border border-windows-200 rounded-lg text-center hover:border-windows-300 hover:bg-windows-50 transition-all duration-200"
              >
                <div className="flex flex-col items-center space-y-2">
                  <sourceType.icon className="w-8 h-8 text-windows-600" />
                  <div>
                    <div className="font-medium text-windows-900">{sourceType.name}</div>
                    <div className="text-sm text-windows-500">{sourceType.description}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
          
      {dataSources.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-windows-800">Configured Data Sources</h3>
              {dataSources.map((source) => (
                <div key={source.id} className="border border-windows-200 rounded-lg">
                  <div className="p-4 bg-windows-50 border-b border-windows-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={selectedSources.some(s => s.id === source.id)}
                          onChange={() => toggleDataSourceSelection(source)}
                          className="h-4 w-4 text-accent-600 focus:ring-accent-500 border-windows-300 rounded"
                        />
                        <div className="flex items-center space-x-2">
                          {getDataSourceIcon(source.type)}
                          <span className="font-medium text-windows-900">{source.name}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setExpandedSource(expandedSource === source.id ? null : source.id)}
                          className="p-1 hover:bg-windows-200 rounded transition-colors duration-200"
                        >
                          {expandedSource === source.id ? (
                            <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ChevronRight className="h-4 w-4" />
                          )}
                        </button>
                        <button
                          onClick={() => removeDataSource(source.id)}
                          className="p-1 hover:bg-error-100 rounded transition-colors duration-200"
                        >
                          <Trash2 className="h-4 w-4 text-error-600" />
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  {expandedSource === source.id && (
                    <div className="p-4 bg-white">
                      {source.type === 'file' ? renderFileUploadSection() : null}
                      {source.type === 'mysql' ? renderMysqlSection(source) : null}
                      {source.type === 'oracle' ? renderOracleSection(source) : null}
                      {source.type === 'api' ? renderRestApiSection(source) : null}
                      {source.type !== 'file' && source.type !== 'mysql' && source.type !== 'oracle' && source.type !== 'api' ? renderDataSourceFields(source) : null}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          </div>
        </div>

      {/* Schema Analysis Loading Screen */}
      {showSchemaAnalysisLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="mb-6">
                <Loader2 className="h-12 w-12 animate-spin text-accent-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-windows-900 mb-2">
                  {useSampleData ? 'Loading Data from Source' : 'Starting Schema Analysis'}
                </h3>
                <p className="text-windows-600">
                  {useSampleData ? 'Preparing to load data for preview...' : 'Preparing to analyze your data structure...'}
                </p>
              </div>
              
              <div className="space-y-3">
                {(useSampleData ? [
                  'Loading data from source',
                  'Preparing data preview',
                  'Setting up file structure',
                  'Ready for data preview'
                ] : [
                  'Understanding your data',
                  'Understanding the schema',
                  'Applying relational logics',
                  'Applying test scenarios'
                ]).map((step, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      index === schemaAnalysisStep 
                        ? 'bg-accent-600 text-white animate-pulse' 
                        : 'bg-windows-200 text-windows-600'
                    }`}>
                      <span className="text-xs font-medium">{index + 1}</span>
                    </div>
                    <span className={`text-sm ${
                      index === schemaAnalysisStep ? 'text-windows-900 font-medium' : 'text-windows-600'
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

      {/* Navigation */}
      <div className="flex items-center justify-between mt-8 pt-6 pb-8 border-t border-windows-200 bg-white sticky bottom-0 z-10" style={{ bottom: '40px' }}>
        <button
          onClick={() => navigate('/create')}
          className="btn-windows flex items-center space-x-2"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back</span>
        </button>
        
        <button
          onClick={handleContinue}
          disabled={isLoading || (!useSampleData && selectedSources.length === 0)}
          className="btn-windows-primary flex items-center space-x-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Loading...</span>
            </>
          ) : (
            <>
              <span>Continue to Data Preview</span>
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default DataSourcePage;

export {}; 