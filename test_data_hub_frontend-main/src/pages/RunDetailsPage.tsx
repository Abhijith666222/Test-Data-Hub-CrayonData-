import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Database, 
  FileText, 
  BarChart3, 
  CheckCircle,
  AlertCircle,
  Clock,
  Calendar,
  Download,
  Eye,
  ArrowLeft,
  RefreshCw,
  Loader2,
  Settings,
  Play,
  Square,
  Trash2
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useNotification } from '../context/NotificationContext';
import { apiService } from '../services/apiService';

const RunDetailsPage: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const { showInfo } = useNotification();
  const [runDetails, setRunDetails] = useState<any>(null);
  const [runFiles, setRunFiles] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (runId) {
      loadRunDetails();
      loadRunFiles();
    }
  }, [runId]);

  const loadRunDetails = async () => {
    if (!runId) return;
    
    setIsLoading(true);
    try {
      const details = await apiService.getRun(runId);
      setRunDetails(details);
      dispatch({ type: 'SET_CURRENT_RUN', payload: details });
    } catch (error) {
      console.error('Failed to load task details:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadRunFiles = async () => {
    if (!runId) return;
    
    try {
      const files = await apiService.getRunFiles(runId);
      setRunFiles(files);
    } catch (error) {
      console.error('Failed to load task files:', error);
    }
  };

  const getStatusBadge = (status: boolean, label: string) => {
    return (
      <span className={`badge-windows ${status ? 'badge-windows-success' : 'badge-windows-error'}`}>
        {status ? '✓' : '✗'} {label}
      </span>
    );
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleRerun = async () => {
    if (!runId) return;
    
    setIsLoading(true);
    try {
      const result = await apiService.runCompletePipeline(runId, 'full');
      if (result?.run_id) {
        navigate(`/run/${result.run_id}`);
      }
    } catch (error) {
      console.error('Failed to rerun:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!runId || !window.confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
      return;
    }
    
    // In a real implementation, this would call an API to delete the run
    showInfo('Info', 'Task deletion is not implemented in demo mode.');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-accent-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-windows-900 mb-2">Loading Task Details</h3>
          <p className="text-windows-600">Fetching information for Task {runId}...</p>
        </div>
      </div>
    );
  }

  if (!runDetails) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-windows-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-windows-900 mb-2">Task Not Found</h3>
        <p className="text-windows-600 mb-6">The requested task could not be found.</p>
        <button
          onClick={() => navigate('/')}
          className="btn-windows-primary"
        >
          Back to Home
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/')}
            className="btn-windows flex items-center space-x-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back</span>
          </button>
          <div>
            <h1 className="text-3xl font-bold text-windows-900">Task {runId}</h1>
            <p className="text-windows-600 mt-1">
              Test Data Environment System
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={loadRunDetails}
            disabled={isLoading}
            className="btn-windows flex items-center space-x-2"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleRerun}
            disabled={isLoading}
            className="btn-windows-primary flex items-center space-x-2"
          >
            <Play className="h-4 w-4" />
            <span>Rerun</span>
          </button>
          <button
            onClick={handleDelete}
            className="btn-windows-error flex items-center space-x-2"
          >
            <Trash2 className="h-4 w-4" />
            <span>Delete</span>
          </button>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card-windows p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-windows-600">Input Data</p>
              <p className="text-2xl font-bold text-windows-900">
                {runDetails.has_input_data ? '✓' : '✗'}
              </p>
            </div>
            <Database className="h-8 w-8 text-accent-600" />
          </div>
        </div>
        
        <div className="card-windows p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-windows-600">Schema Analysis</p>
              <p className="text-2xl font-bold text-windows-900">
                {runDetails.has_schema ? '✓' : '✗'}
              </p>
            </div>
            <FileText className="h-8 w-8 text-success-600" />
          </div>
        </div>
        
        <div className="card-windows p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-windows-600">Synthetic Data</p>
              <p className="text-2xl font-bold text-windows-900">
                {runDetails.has_synthetic_data ? '✓' : '✗'}
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-warning-600" />
          </div>
        </div>
        
        <div className="card-windows p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-windows-600">Validation</p>
              <p className="text-2xl font-bold text-windows-900">
                {runDetails.has_validation ? '✓' : '✗'}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-error-600" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card-windows">
        <div className="border-b border-windows-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: 'Overview', icon: Eye },
              { id: 'files', label: 'Files', icon: FileText },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-accent-500 text-accent-600'
                      : 'border-transparent text-windows-500 hover:text-windows-700 hover:border-windows-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-windows-900 mb-4">Run Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-windows-500" />
                      <span className="text-sm text-windows-600">Created:</span>
                      <span className="text-sm font-medium text-windows-900">
                        {formatDate(runDetails.created_at)}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-windows-500" />
                      <span className="text-sm text-windows-600">Last Modified:</span>
                      <span className="text-sm font-medium text-windows-900">
                        {formatDate(runDetails.updated_at || runDetails.created_at)}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-windows-600">Status:</span>
                      <div className="flex space-x-2">
                        {getStatusBadge(runDetails.has_input_data, 'Input')}
                        {getStatusBadge(runDetails.has_schema, 'Schema')}
                        {getStatusBadge(runDetails.has_synthetic_data, 'Data')}
                        {getStatusBadge(runDetails.has_validation, 'Validation')}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-windows-900 mb-4">Quick Actions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => navigate('/schema-analysis')}
                    className="btn-windows flex items-center space-x-2"
                  >
                    <FileText className="h-4 w-4" />
                    <span>View Test Scenarios</span>
                  </button>
                  <button
                    onClick={() => navigate('/data-generation')}
                    className="btn-windows flex items-center space-x-2"
                  >
                    <BarChart3 className="h-4 w-4" />
                    <span>View Generated Data</span>
                  </button>
                  <button
                    onClick={() => navigate('/data-preview')}
                    className="btn-windows flex items-center space-x-2"
                  >
                    <Eye className="h-4 w-4" />
                    <span>Data Preview</span>
                  </button>
                  <button
                    onClick={() => navigate('/destination')}
                    className="btn-windows flex items-center space-x-2"
                  >
                    <Download className="h-4 w-4" />
                    <span>Push to System</span>
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'files' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-windows-900">Generated Files</h3>
              
              {runFiles ? (
                <div className="space-y-4">
                  {Object.entries(runFiles.files || {}).map(([category, files]: [string, any]) => (
                    <div key={category} className="border border-windows-200 rounded-lg">
                      <div className="p-4 bg-windows-50 border-b border-windows-200">
                        <h4 className="font-medium text-windows-900 capitalize">
                          {category.replace('_', ' ')} Files
                        </h4>
                      </div>
                      <div className="p-4">
                        {Array.isArray(files) && files.length > 0 ? (
                          <div className="space-y-2">
                            {files.map((file: any, index: number) => (
                              <div key={index} className="flex items-center justify-between p-3 bg-windows-50 rounded-md">
                                <div className="flex items-center space-x-3">
                                  <FileText className="h-4 w-4 text-accent-600" />
                                  <span className="font-medium text-windows-900">{file.name}</span>
                                  {file.size && (
                                    <span className="text-sm text-windows-600">
                                      ({(file.size / 1024).toFixed(1)} KB)
                                    </span>
                                  )}
                                </div>
                                <button className="btn-windows text-xs px-3 py-1">
                                  Download
                                </button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-windows-600 text-sm">No files available</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-windows-400 mx-auto mb-4" />
                  <p className="text-windows-600">No files found for this run</p>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-windows-900">Run Configuration</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium text-windows-900">General Settings</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="form-label-windows">Task ID</label>
                      <input
                        type="text"
                        value={runId}
                        readOnly
                        className="input-windows bg-windows-50"
                      />
                    </div>
                    <div>
                      <label className="form-label-windows">Created Date</label>
                      <input
                        type="text"
                        value={formatDate(runDetails.created_at)}
                        readOnly
                        className="input-windows bg-windows-50"
                      />
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium text-windows-900">Status Information</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-windows-600">Input Data:</span>
                      {getStatusBadge(runDetails.has_input_data, '')}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-windows-600">Schema Analysis:</span>
                      {getStatusBadge(runDetails.has_schema, '')}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-windows-600">Synthetic Data:</span>
                      {getStatusBadge(runDetails.has_synthetic_data, '')}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-windows-600">Validation:</span>
                      {getStatusBadge(runDetails.has_validation, '')}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RunDetailsPage;

export {}; 