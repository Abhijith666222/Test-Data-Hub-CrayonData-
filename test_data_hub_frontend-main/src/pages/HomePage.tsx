import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Database, 
  FileText, 
  BarChart3, 
  Play,
  Calendar,
  Clock,
  ArrowRight,
  RefreshCw,
  Workflow,
  GitBranch,
  Zap,
  Eye,
  Shield,
  Target,
  TestTube,
  Activity,
  Globe
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { apiService } from '../services/apiService';
import PipelineDiagram from '../components/PipelineDiagram';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { state, dispatch } = useApp();

  // Task descriptions from PipelineDiagram
  const taskDescriptions: { [key: number]: string } = {
    1: 'Collect and process credit card data from Prime system',
    2: 'Generate synthetic data and continue modifying Workspace DB',
    3: 'Add functional test scenarios and continue modifying Workspace DB',
    4: 'Load from Workspace DB and push to multiple destination servers'
  };

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const runs = await apiService.getRuns();
      dispatch({ type: 'SET_RUNS', payload: runs });
    } catch (error) {
      console.error('Failed to load runs:', error);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const getStatusBadges = (run: any) => {
    const badges = [];
    if (run.has_schema) badges.push({ label: 'Schema', color: 'success' });
    if (run.has_synthetic_data) badges.push({ label: 'Data', color: 'info' });
    if (run.has_validation) badges.push({ label: 'Validation', color: 'warning' });
    if (run.has_input_data) badges.push({ label: 'Input', color: 'accent' });
    return badges;
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-windows-900">Welcome to Test Data Hub</h1>
          <p className="text-windows-600 mt-2">
            AI-powered synthetic data generation and validation system
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadRuns}
            className="btn-windows flex items-center space-x-2"
            disabled={state.isLoading}
          >
            <RefreshCw size={16} className={state.isLoading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => navigate('/create')}
            className="btn-windows-primary flex items-center space-x-2"
          >
            <Plus size={16} />
            <span>Create New System</span>
          </button>
          <button
            onClick={() => navigate('/create-pipeline')}
            className="btn-windows flex items-center space-x-2"
          >
            <GitBranch size={16} />
            <span>Create Pipeline</span>
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card-windows p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-windows-600">Total Tasks</p>
              <p className="text-2xl font-bold text-windows-900">{state.runs.length}</p>
            </div>
            <Database className="h-8 w-8 text-accent-600" />
          </div>
        </div>
        
        <div className="card-windows p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-windows-600">With Schema</p>
              <p className="text-2xl font-bold text-windows-900">
                {state.runs.filter(r => r.has_schema).length}
              </p>
            </div>
            <FileText className="h-8 w-8 text-success-600" />
          </div>
        </div>
        
        <div className="card-windows p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-windows-600">With Data</p>
              <p className="text-2xl font-bold text-windows-900">
                {state.runs.filter(r => r.has_synthetic_data).length}
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-warning-600" />
          </div>
        </div>
        
        <div className="card-windows p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-windows-600">Validated</p>
              <p className="text-2xl font-bold text-windows-900">
                {state.runs.filter(r => r.has_validation).length}
              </p>
            </div>
            <Play className="h-8 w-8 text-error-600" />
          </div>
        </div>
      </div>

      {/* Pipeline Diagram */}
      <PipelineDiagram />
      
      {/* Create Custom Task Pipeline */}
      <div className="card-windows">
        <div className="p-6 border-b border-windows-200">
          <h2 className="text-xl font-semibold text-windows-900 flex items-center space-x-2">
            <Workflow className="h-5 w-5 text-accent-600" />
            <span>Create Custom Task Pipeline</span>
          </h2>
          <p className="text-windows-600 mt-1">
            Build custom data processing pipelines by combining different tasks and workflows
          </p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="text-center p-6 bg-gradient-to-br from-accent-50 to-blue-50 rounded-lg border border-accent-200">
              <div className="p-3 bg-accent-100 rounded-lg w-fit mx-auto mb-4">
                <GitBranch className="h-8 w-8 text-accent-600" />
              </div>
              <h3 className="text-lg font-semibold text-windows-900 mb-2">Task Pipeline Builder</h3>
              <p className="text-windows-600 text-sm mb-4">
                Create custom workflows by selecting from a library of data processing tasks
              </p>
              <div className="space-y-2 text-xs text-windows-500 mb-4">
                <div className="flex items-center justify-center space-x-2">
                  <Database className="h-3 w-3" />
                  <span>Data Ingestion</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <BarChart3 className="h-3 w-3" />
                  <span>Data Processing</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <Shield className="h-3 w-3" />
                  <span>Data Validation</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <Target className="h-3 w-3" />
                  <span>Data Delivery</span>
                </div>
              </div>
              <button
                onClick={() => navigate('/create-pipeline')}
                className="btn-windows-primary flex items-center space-x-2 mx-auto"
              >
                <Plus size={16} />
                <span>Build Pipeline</span>
              </button>
            </div>
            
            <div className="text-center p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
              <div className="p-3 bg-green-100 rounded-lg w-fit mx-auto mb-4">
                <Zap className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-windows-900 mb-2">Pre-built Templates</h3>
              <p className="text-windows-600 text-sm mb-4">
                Use ready-made pipeline templates for common data processing scenarios
              </p>
              <div className="space-y-2 text-xs text-windows-500 mb-4">
                <div className="flex items-center justify-center space-x-2">
                  <FileText className="h-3 w-3" />
                  <span>ETL Pipeline</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <TestTube className="h-3 w-3" />
                  <span>Data Quality</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <Activity className="h-3 w-3" />
                  <span>Monitoring</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <Globe className="h-3 w-3" />
                  <span>API Integration</span>
                </div>
              </div>
              <button
                onClick={() => navigate('/create-pipeline')}
                className="btn-windows flex items-center space-x-2 mx-auto"
              >
                <Eye size={16} />
                <span>Browse Templates</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Existing Runs */}
      <div className="card-windows">
        <div className="p-6 border-b border-windows-200">
          <h2 className="text-xl font-semibold text-windows-900">Existing Tasks</h2>
          <p className="text-windows-600 mt-1">
            Click on any task to view details and manage your test data
          </p>
        </div>
        
        <div className="p-6">
          {state.isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="spinner-windows w-8 h-8"></div>
              <span className="ml-3 text-windows-600">Loading tasks...</span>
            </div>
          ) : state.runs.length === 0 ? (
            <div className="text-center py-12">
              <Database className="h-12 w-12 text-windows-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-windows-900 mb-2">No tasks found</h3>
              <p className="text-windows-600 mb-6">
                Get started by creating your first test data system
              </p>
              <button
                onClick={() => navigate('/create')}
                className="btn-windows-primary flex items-center space-x-2 mx-auto"
              >
                <Plus size={16} />
                <span>Create First System</span>
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
              {state.runs.map((run) => (
                <div
                  key={run.run_id}
                  className="card-windows p-6 hover:shadow-windows-lg cursor-pointer transition-all duration-200"
                  onClick={() => navigate(`/run/${run.run_id}`)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-accent-100 rounded-lg">
                        <Database className="h-6 w-6 text-accent-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-windows-900">Task {run.run_id}</h3>
                        <p className="text-sm text-windows-600">Test Data System</p>
                        {taskDescriptions[Number(run.run_id)] && (
                          <p className="text-xs text-windows-500 mt-1">
                            {taskDescriptions[Number(run.run_id)]}
                          </p>
                        )}
                      </div>
                    </div>
                    <ArrowRight className="h-5 w-5 text-windows-400" />
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2 text-sm text-windows-600">
                      <Calendar size={14} />
                      <span>{formatDate(run.created_at)}</span>
                    </div>
                    
                    <div className="flex flex-wrap gap-2">
                      {getStatusBadges(run).map((badge, index) => (
                        <span
                          key={index}
                          className={`badge-windows badge-windows-${badge.color}`}
                        >
                          {badge.label}
                        </span>
                      ))}
                    </div>
                    
                    <div className="flex items-center justify-between pt-3 border-t border-windows-100">
                      <div className="flex items-center space-x-4 text-sm text-windows-600">
                        <div className="flex items-center space-x-1">
                          <FileText size={14} />
                          <span>{run.has_schema ? 'Schema' : 'No Schema'}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <BarChart3 size={14} />
                          <span>{run.has_synthetic_data ? 'Data' : 'No Data'}</span>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/run/${run.run_id}`);
                        }}
                        className="btn-windows text-xs px-3 py-1"
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>



      {/* Quick Actions */}
      <div className="card-windows">
        <div className="p-6 border-b border-windows-200">
          <h2 className="text-xl font-semibold text-windows-900">Quick Actions</h2>
          <p className="text-windows-600 mt-1">
            Common tasks to get you started quickly
          </p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => navigate('/create')}
              className="card-windows p-6 text-left hover:shadow-windows-lg transition-all duration-200 group"
            >
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-success-100 rounded-lg group-hover:bg-success-200 transition-colors duration-200">
                  <Plus className="h-6 w-6 text-success-600" />
                </div>
                <h3 className="font-semibold text-windows-900">Create New System</h3>
              </div>
              <p className="text-windows-600 text-sm">
                Start a new test data generation project with AI-powered analysis
              </p>
            </button>
            
            <button
              onClick={() => navigate('/overview')}
              className="card-windows p-6 text-left hover:shadow-windows-lg transition-all duration-200 group"
            >
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-info-100 rounded-lg group-hover:bg-info-200 transition-colors duration-200">
                  <FileText className="h-6 w-6 text-info-600" />
                </div>
                <h3 className="font-semibold text-windows-900">Product Overview</h3>
              </div>
              <p className="text-windows-600 text-sm">
                Learn about features and capabilities of the Test Data Environment
              </p>
            </button>
            
            <button
              onClick={loadRuns}
              className="card-windows p-6 text-left hover:shadow-windows-lg transition-all duration-200 group"
            >
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-warning-100 rounded-lg group-hover:bg-warning-200 transition-colors duration-200">
                  <RefreshCw className="h-6 w-6 text-warning-600" />
                </div>
                <h3 className="font-semibold text-windows-900">Refresh Data</h3>
              </div>
              <p className="text-windows-600 text-sm">
                Update the list of available runs and their current status
              </p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;

export {}; 