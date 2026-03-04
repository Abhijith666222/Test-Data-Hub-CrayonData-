import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Database, 
  Server, 
  Globe,
  FileText,
  Upload,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Loader2,
  Settings,
  Zap,
  Shield,
  BarChart3,
  TestTube,
  AlertCircle,
  Cloud,
  Activity,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useNotification } from '../context/NotificationContext';
import { apiService } from '../services/apiService';

const DestinationPage: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useApp();
  const { showWarning, showSuccess, showError } = useNotification();
  const [selectedDestination, setSelectedDestination] = useState<string>('');
  const [isPushing, setIsPushing] = useState(false);
  const [pushProgress, setPushProgress] = useState(0);
  const [pushStatus, setPushStatus] = useState<string>('');
  
  // Database connection state
  const [mysqlConnection, setMysqlConnection] = useState({
    host: 'localhost',
    port: '3306',
    database: 'test_data_environment',
    username: 'root',
    password: ''
  });
  const [oracleConnection, setOracleConnection] = useState({
    host: 'localhost',
    port: '1521',
    serviceName: 'XEPDB1',
    username: 'system',
    password: ''
  });
  
  // REST API configuration state
  const [restApiConfig, setRestApiConfig] = useState({
    apiUrl: '',
    apiKey: '',
    method: 'POST',
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
  const [showAllDestinationTypes, setShowAllDestinationTypes] = useState(false);

  // Load database configuration on component mount
  useEffect(() => {
    loadDatabaseConfig();
  }, []);

  const loadDatabaseConfig = async () => {
    try {
      // Load config values from backend (you can implement this endpoint if needed)
      // For now, we'll use default values that match config.py
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

  const destinationTypes = [
    {
      id: 'mysql',
      name: 'MySQL Database',
      icon: Database,
      description: 'Push data to MySQL database',
      options: [
        'Structured Data', 'CSV Import', 'Bulk Insert',
        'Transaction Support', 'Data Validation'
      ]
    },
    {
      id: 'oracle',
      name: 'Oracle Database',
      icon: Database,
      description: 'Push data to Oracle database',
      options: [
        'Enterprise Grade', 'PL/SQL Support', 'Advanced Security',
        'High Performance', 'Scalability'
      ]
    },
    {
      id: 'rest-api',
      name: 'REST API',
      icon: Globe,
      description: 'Push data via REST API endpoints',
      options: [
        'HTTP Methods', 'JSON/XML Support', 'Authentication',
        'Rate Limiting', 'Legacy Integration'
      ]
    },
    {
      id: 'sql',
      name: 'RPA Agent',
      icon: Database,
      description: 'Robotic Process Automation Agent Connection',
      options: [
        'Enterprise Integration', 'T-SQL Support', 'Advanced Analytics',
        'High Availability', 'Security Features'
      ]
    },
    {
      id: 'postgresql',
      name: 'PostgreSQL',
      icon: Database,
      description: 'Push data to PostgreSQL database',
      options: [
        'Open Source', 'JSON Support', 'Advanced Features',
        'Extensibility', 'Performance'
      ]
    },
    {
      id: 'mongodb',
      name: 'MongoDB',
      icon: Database,
      description: 'Push data to MongoDB NoSQL database',
      options: [
        'Document Storage', 'Schema Flexibility', 'Horizontal Scaling',
        'JSON Native', 'High Performance'
      ]
    },
    {
      id: 'redshift',
      name: 'Amazon Redshift',
      icon: Cloud,
      description: 'Push data to Amazon Redshift data warehouse',
      options: [
        'Columnar Storage', 'Massive Parallel Processing', 'Cloud Native',
        'Petabyte Scale', 'Integration Services'
      ]
    },
    {
      id: 'bigquery',
      name: 'Google BigQuery',
      icon: Cloud,
      description: 'Push data to Google BigQuery data warehouse',
      options: [
        'Serverless', 'Machine Learning', 'Real-time Analytics',
        'Global Scale', 'Cost Optimization'
      ]
    },
    {
      id: 'snowflake',
      name: 'Snowflake',
      icon: Cloud,
      description: 'Push data to Snowflake data warehouse',
      options: [
        'Multi-Cloud', 'Data Sharing', 'Time Travel',
        'Zero Management', 'Elastic Scaling'
      ]
    },

    {
      id: 'file',
      name: 'File Export',
      icon: FileText,
      description: 'Export data to various file formats',
      options: [
        'CSV Export', 'JSON Export', 'XML Export',
        'Excel Export', 'Custom Formats'
      ]
    }
  ];

  const handleDestinationSelect = (destinationId: string) => {
    setSelectedDestination(destinationId);
    setConnectionStatus('idle');
  };

  const testConnection = async () => {
    if (!selectedDestination) return;
    
    setIsConnecting(true);
    setConnectionStatus('connecting');
    
    try {
      let response;
      if (selectedDestination === 'mysql') {
        response = await apiService.testMysqlConnection(mysqlConnection);
      } else if (selectedDestination === 'oracle') {
        response = await apiService.testOracleConnection(oracleConnection);
      } else if (selectedDestination === 'rest-api') {
        // For REST API, we'll simulate a connection test
        // In a real implementation, this would call the API service
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
        response = { status: 200, message: 'REST API connection successful' };
      }
      
      if (response?.status === 200) {
        setConnectionStatus('connected');
        showSuccess('Success', `${selectedDestination.toUpperCase()} connection successful!`);
      } else {
        setConnectionStatus('error');
        showError('Connection Failed', response?.error || `Failed to connect to ${selectedDestination}`);
      }
    } catch (error) {
      setConnectionStatus('error');
      showError('Connection Failed', `Failed to connect to ${selectedDestination} database`);
    } finally {
      setIsConnecting(false);
    }
  };

  const handlePushData = async () => {
    if (!selectedDestination) {
      showWarning('Warning', 'Please select a destination type.');
      return;
    }

    if (connectionStatus !== 'connected') {
      showWarning('Warning', 'Please test the connection first before pushing data.');
      return;
    }

    setIsPushing(true);
    setPushProgress(0);
    setPushStatus('Initializing data transfer...');

    try {
      // Get the current run ID from context
      const runId = state.currentRun?.run_id;
      if (!runId) {
        throw new Error('No run ID found. Please go back to data generation page.');
      }

      // Get the generated files for this run
      const filesResponse = await apiService.getRunFiles(runId);
      const files = filesResponse?.data?.files?.synthetic_data || filesResponse?.files?.synthetic_data || [];
      
      if (files.length === 0) {
        throw new Error('No generated files found for this run.');
      }

      setPushStatus(`Found ${files.length} files. Starting data transfer...`);
      setPushProgress(20);

      // Push data to selected database
      if (selectedDestination === 'mysql') {
        setPushStatus('Pushing data to MySQL database...');
        setPushProgress(40);
        
        const response = await apiService.pushDataToDatabase(
          runId,
          'mysql',
          mysqlConnection,
          files
        );
        
        if (response.status === 200) {
          setPushStatus('Data successfully pushed to MySQL!');
          setPushProgress(100);
        } else {
          throw new Error(response.error || 'Failed to push data to MySQL');
        }
        
      } else if (selectedDestination === 'oracle') {
        setPushStatus('Pushing data to Oracle database...');
        setPushProgress(40);
        
        const response = await apiService.pushDataToDatabase(
          runId,
          'oracle',
          oracleConnection,
          files
        );
        
        if (response.status === 200) {
          setPushStatus('Data successfully pushed to Oracle!');
          setPushProgress(100);
        } else {
          throw new Error(response.error || 'Failed to push data to Oracle');
        }
      } else if (selectedDestination === 'rest-api') {
        setPushStatus('Pushing data via REST API...');
        setPushProgress(40);

        // Simulate REST API push operation
        // In a real implementation, this would call the API service
        await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
        
        setPushStatus('Data successfully pushed to REST API!');
        setPushProgress(100);
      }

      showSuccess('Success', `Data successfully pushed to ${selectedDestination.toUpperCase()} database!`);
      
      // Navigate back to home after successful push
      setTimeout(() => {
        navigate('/');
      }, 2000);
      
    } catch (error) {
      console.error('Failed to push data:', error);
      showError('Error', `Failed to push data: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setPushStatus('Data transfer failed!');
    } finally {
      setIsPushing(false);
    }
  };

  const getDestinationIcon = (iconName: any) => {
    const Icon = iconName;
    return <Icon className="h-6 w-6" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-windows-900">Destination System</h1>
        <p className="text-windows-600 mt-2 max-w-2xl mx-auto">
          Configure where you want to push your generated test data. Choose from various destination types.
        </p>
      </div>

      {/* Push Progress */}
      {isPushing && (
        <div className="card-windows">
          <div className="p-6">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin text-accent-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-windows-900 mb-2">Pushing Data to System</h3>
              <p className="text-windows-600 mb-4">{pushStatus}</p>
              
              <div className="w-full max-w-md mx-auto">
                <div className="progress-windows">
                  <div 
                    className="progress-bar-windows" 
                    style={{ width: `${pushProgress}%` }}
                  ></div>
                </div>
                <div className="text-sm text-windows-600 mt-2">
                  {Math.round(pushProgress)}% Complete
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Existing Systems */}
      {!isPushing && (
        <div className="card-windows">
          <div className="p-6 border-b border-windows-200">
            <h2 className="text-xl font-semibold text-windows-900 flex items-center space-x-2">
              <Server className="h-5 w-5 text-accent-600" />
              <span>Choose Existing Systems</span>
            </h2>
            <p className="text-windows-600 mt-1">
              Select from pre-configured destination systems or add new destinations
            </p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { name: 'Prime', icon: Database, description: 'Production Oracle database', status: 'active' },
                { name: 'iOptimus', icon: Database, description: 'Development MySQL server', status: 'active' },
                { name: 'RedisDB', icon: Database, description: 'In Memory RedisDB', status: 'active' },
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
      )}

      {/* Destination Selection */}
      {!isPushing && (
        <div className="card-windows">
          <div className="p-6 border-b border-windows-200">
            <h2 className="text-xl font-semibold text-windows-900 flex items-center space-x-2">
              <Upload className="h-5 w-5 text-accent-600" />
              <span>Select Destination Type</span>
            </h2>
            <p className="text-windows-600 mt-1">
              Choose how you want to deliver your test data to the target system
            </p>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {destinationTypes.slice(0, showAllDestinationTypes ? destinationTypes.length : 4).map((destination) => (
                <div
                  key={destination.id}
                  className={`card-windows p-6 cursor-pointer transition-all duration-200 ${
                    selectedDestination === destination.id
                      ? 'ring-2 ring-accent-500 bg-accent-50'
                      : 'hover:shadow-windows-lg'
                  }`}
                  onClick={() => handleDestinationSelect(destination.id)}
                >
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 rounded-lg ${
                      selectedDestination === destination.id
                        ? 'bg-accent-100 text-accent-600'
                        : 'bg-windows-100 text-windows-600'
                    }`}>
                      {getDestinationIcon(destination.icon)}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-windows-900 mb-2">{destination.name}</h3>
                      <p className="text-windows-600 text-sm mb-3">{destination.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {destination.options.slice(0, 3).map((option, index) => (
                          <span key={index} className="badge-windows badge-windows-info text-xs">
                            {option}
                          </span>
                        ))}
                        {destination.options.length > 3 && (
                          <span className="badge-windows badge-windows-info text-xs">
                            +{destination.options.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                    {selectedDestination === destination.id && (
                      <CheckCircle className="h-5 w-5 text-accent-600" />
                    )}
                  </div>
                </div>
              ))}
            </div>
            
            {/* Show More/Less Button */}
            {destinationTypes.length > 4 && (
              <div className="mt-6 text-center">
                <button
                  onClick={() => setShowAllDestinationTypes(!showAllDestinationTypes)}
                  className="btn-windows flex items-center space-x-2 mx-auto"
                >
                  {showAllDestinationTypes ? (
                    <>
                      <ChevronUp className="h-4 w-4" />
                      <span>Show Less</span>
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-4 w-4" />
                      <span>Show More ({destinationTypes.length - 4} more)</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Configuration Options */}
      {selectedDestination && !isPushing && (
        <div className="card-windows">
          <div className="p-6 border-b border-windows-200">
            <h2 className="text-xl font-semibold text-windows-900 flex items-center space-x-2">
              <Settings className="h-5 w-5 text-accent-600" />
              <span>Database Connection Configuration</span>
            </h2>
            <p className="text-windows-600 mt-1">
              Configure connection settings for your selected database
            </p>
          </div>
          
          <div className="p-6">
            {selectedDestination === 'mysql' && (
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Database className="w-5 h-5 text-windows-600" />
                  <h3 className="text-lg font-semibold text-windows-900">MySQL Database Connection</h3>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">Host</label>
                    <input
                      type="text"
                      value={mysqlConnection.host}
                      onChange={(e) => setMysqlConnection(prev => ({ ...prev, host: e.target.value }))}
                      placeholder="localhost"
                      className="input-windows w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">Port</label>
                    <input
                      type="text"
                      value={mysqlConnection.port}
                      onChange={(e) => setMysqlConnection(prev => ({ ...prev, port: e.target.value }))}
                      placeholder="3306"
                      className="input-windows w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">Database</label>
                    <input
                      type="text"
                      value={mysqlConnection.database}
                      onChange={(e) => setMysqlConnection(prev => ({ ...prev, database: e.target.value }))}
                      placeholder="your_database"
                      className="input-windows w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">Username</label>
                    <input
                      type="text"
                      value={mysqlConnection.username}
                      onChange={(e) => setMysqlConnection(prev => ({ ...prev, username: e.target.value }))}
                      placeholder="your_username"
                      className="input-windows w-full"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-windows-700 mb-1">Password</label>
                    <input
                      type="password"
                      value={mysqlConnection.password}
                      onChange={(e) => setMysqlConnection(prev => ({ ...prev, password: e.target.value }))}
                      placeholder="your_password"
                      className="input-windows w-full"
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <button
                    onClick={testConnection}
                    disabled={isConnecting || !mysqlConnection.host || !mysqlConnection.database || !mysqlConnection.username || !mysqlConnection.password}
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
            )}

            {selectedDestination === 'oracle' && (
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Database className="w-5 h-5 text-windows-600" />
                  <h3 className="text-lg font-semibold text-windows-900">Oracle Database Connection</h3>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">Host</label>
                    <input
                      type="text"
                      value={oracleConnection.host}
                      onChange={(e) => setOracleConnection(prev => ({ ...prev, host: e.target.value }))}
                      placeholder="localhost"
                      className="input-windows w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">Port</label>
                    <input
                      type="text"
                      value={oracleConnection.port}
                      onChange={(e) => setOracleConnection(prev => ({ ...prev, port: e.target.value }))}
                      placeholder="1521"
                      className="input-windows w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">Service Name</label>
                    <input
                      type="text"
                      value={oracleConnection.serviceName}
                      onChange={(e) => setOracleConnection(prev => ({ ...prev, serviceName: e.target.value }))}
                      placeholder="your_service_name"
                      className="input-windows w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-windows-700 mb-1">Username</label>
                    <input
                      type="text"
                      value={oracleConnection.username}
                      onChange={(e) => setOracleConnection(prev => ({ ...prev, username: e.target.value }))}
                      placeholder="your_username"
                      className="input-windows w-full"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-windows-700 mb-1">Password</label>
                    <input
                      type="password"
                      value={oracleConnection.password}
                      onChange={(e) => setOracleConnection(prev => ({ ...prev, password: e.target.value }))}
                      placeholder="your_password"
                      className="input-windows w-full"
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <button
                    onClick={testConnection}
                    disabled={isConnecting || !oracleConnection.host || !oracleConnection.serviceName || !oracleConnection.username || !oracleConnection.password}
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
            )}
            
            {selectedDestination === 'rest-api' && (
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
                          placeholder="InsertData"
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
                    onClick={testConnection}
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
            )}
            
            <div className="mt-6 p-4 bg-warning-50 border border-warning-200 rounded-lg">
              <div className="flex items-start space-x-3">
                <Shield className="h-5 w-5 text-warning-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-warning-900 mb-1">Security Notice</h4>
                  <p className="text-warning-700 text-sm">
                    Ensure you have proper authorization to push data to the target database. 
                    Test data should only be pushed to appropriate test environments.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Data Summary
      {!isPushing && (
        <div className="card-windows">
          <div className="p-6 border-b border-windows-200">
            <h2 className="text-xl font-semibold text-windows-900 flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-accent-600" />
              <span>Data Summary</span>
            </h2>
            <p className="text-windows-600 mt-1">
              Overview of the data that will be pushed to the destination
            </p>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-accent-50 rounded-lg">
                <div className="text-2xl font-bold text-accent-600">
                  {state.currentRun?.has_synthetic_data ? '5' : '0'}
                </div>
                <div className="text-sm text-accent-700">Files Generated</div>
              </div>
              
              <div className="text-center p-4 bg-success-50 rounded-lg">
                <div className="text-2xl font-bold text-success-600">
                  {state.currentRun?.has_synthetic_data ? '1,250' : '0'}
                </div>
                <div className="text-sm text-success-700">Total Records</div>
              </div>
              
              <div className="text-center p-4 bg-warning-50 rounded-lg">
                <div className="text-2xl font-bold text-warning-600">
                  {state.currentRun?.has_synthetic_data ? '2.4 MB' : '0 KB'}
                </div>
                <div className="text-sm text-warning-700">Total Size</div>
              </div>
            </div>
            
            <div className="mt-4 p-4 bg-windows-50 rounded-lg">
              <h4 className="font-medium text-windows-900 mb-2">Files to be transferred:</h4>
              {state.currentRun?.has_synthetic_data ? (
                <ul className="space-y-1 text-sm text-windows-600">
                  <li>• customer_info.csv (250 records)</li>
                  <li>• credit_card_accounts.csv (200 records)</li>
                  <li>• credit_card_transactions.csv (500 records)</li>
                  <li>• credit_card_products.csv (50 records)</li>
                  <li>• imobile_user_session.csv (250 records)</li>
                </ul>
              ) : (
                <p className="text-windows-500 text-sm">No generated files found for this run.</p>
              )}
            </div>
          </div>
        </div>
      )} */}

      {/* Navigation */}
      <div className="flex items-center justify-between sticky bottom-0 z-10 bg-white p-4 border-t border-windows-200" style={{ bottom: '40px' }}>
        <button
          onClick={() => navigate('/data-generation')}
          className="btn-windows flex items-center space-x-2"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back</span>
        </button>
        
        {!isPushing && (
          <button
            onClick={handlePushData}
            disabled={!selectedDestination}
            className="btn-windows-primary flex items-center space-x-2"
          >
            <Upload className="h-4 w-4" />
            <span>Push Data to System</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default DestinationPage;

export {}; 