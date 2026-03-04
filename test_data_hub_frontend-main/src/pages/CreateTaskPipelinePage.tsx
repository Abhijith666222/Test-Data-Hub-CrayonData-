import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Database, 
  FileText, 
  Globe,
  Plus,
  Trash2,
  ArrowLeft,
  GitBranch,
  Shield,
  Target,
  TestTube,
  BarChart3,
  CheckCircle,
  Globe as GlobeIcon,
  Save,
  CheckCircle2
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import PipelineDiagram from '../components/PipelineDiagram';

interface PipelineTask {
  id: string;
  name: string;
  description: string;
  icon: any;
  category: string;
}

interface PipelineStep {
  id: string;
  task: PipelineTask;
  order: number;
}

interface Pipeline {
  id: string;
  name: string;
  description: string;
  steps: PipelineStep[];
  createdAt: string;
  status: 'draft' | 'saved' | 'running' | 'completed';
}

const CreateTaskPipelinePage: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useApp();
  
  const [pipelineSteps, setPipelineSteps] = useState<PipelineStep[]>([]);
  const [pipelineName, setPipelineName] = useState('');
  const [pipelineDescription, setPipelineDescription] = useState('');
  const [savedPipelines, setSavedPipelines] = useState<Pipeline[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Simple task list
  const availableTasks: PipelineTask[] = [
    {
      id: 'database-connection',
      name: 'Database Connection',
      description: 'Connect to databases',
      icon: Database,
      category: 'Data Ingestion'
    },
    {
      id: 'api-fetch',
      name: 'API Fetch',
      description: 'Fetch data from APIs',
      icon: GlobeIcon,
      category: 'Data Ingestion'
    },
    {
      id: 'schema-analysis',
      name: 'Schema Analysis',
      description: 'Analyze data structure',
      icon: Shield,
      category: 'Processing'
    },
    {
      id: 'business-logic',
      name: 'Business Logic',
      description: 'Generate business rules',
      icon: Target,
      category: 'Processing'
    },
    {
      id: 'test-scenarios',
      name: 'Test Scenarios',
      description: 'Generate test scenarios',
      icon: TestTube,
      category: 'Processing'
    },
    {
      id: 'synthetic-data',
      name: 'Synthetic Data',
      description: 'Generate synthetic data',
      icon: BarChart3,
      category: 'Processing'
    },
    {
      id: 'database-export',
      name: 'Database Export',
      description: 'Export to databases',
      icon: Database,
      category: 'Delivery'
    }
  ];

  const addTaskToPipeline = (task: PipelineTask) => {
    const newStep: PipelineStep = {
      id: `${task.id}-${Date.now()}`,
      task,
      order: pipelineSteps.length
    };
    setPipelineSteps([...pipelineSteps, newStep]);
  };

  const removeTaskFromPipeline = (stepId: string) => {
    setPipelineSteps(pipelineSteps.filter(step => step.id !== stepId));
  };

  const clearPipeline = () => {
    setPipelineSteps([]);
    setPipelineName('');
    setPipelineDescription('');
  };

  const savePipeline = async () => {
    if (!pipelineName.trim()) {
      alert('Please enter a pipeline name');
      return;
    }
    if (pipelineSteps.length === 0) {
      alert('Please add at least one task to the pipeline');
      return;
    }

    setIsSaving(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const newPipeline: Pipeline = {
      id: `pipeline-${Date.now()}`,
      name: pipelineName.trim(),
      description: pipelineDescription.trim() || 'No description provided',
      steps: [...pipelineSteps],
      createdAt: new Date().toISOString(),
      status: 'saved'
    };

    setSavedPipelines(prev => [newPipeline, ...prev]);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
    setIsSaving(false);
  };

  const getPipelineSummary = () => {
    if (pipelineSteps.length === 0) return null;
    
    const categorySet = new Set<string>();
    pipelineSteps.forEach(step => categorySet.add(step.task.category));
    const categories = Array.from(categorySet);
    const totalSteps = pipelineSteps.length;
    
    return {
      totalSteps,
      categories,
      estimatedTime: `${totalSteps * 2}-${totalSteps * 5} minutes`,
      complexity: totalSteps <= 3 ? 'Simple' : totalSteps <= 6 ? 'Medium' : 'Complex'
    };
  };

  const summary = getPipelineSummary();

  return (
    <div className="h-full flex flex-col">
      {/* Pipeline Summary Header */}
      {summary && (
        <div className="bg-gradient-to-r from-accent-50 to-blue-50 border-b border-accent-200 p-4">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-accent-100 rounded-lg">
                    <GitBranch className="h-5 w-5 text-accent-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-windows-900">Pipeline Summary</h2>
                    <p className="text-sm text-windows-600">Current pipeline configuration</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-6 text-sm">
                  <div className="text-center">
                    <div className="text-lg font-bold text-accent-600">{summary.totalSteps}</div>
                    <div className="text-windows-600">Total Steps</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-blue-600">{summary.categories.length}</div>
                    <div className="text-windows-600">Categories</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-600">{summary.estimatedTime}</div>
                    <div className="text-windows-600">Est. Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-purple-600">{summary.complexity}</div>
                    <div className="text-windows-600">Complexity</div>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={savePipeline}
                  disabled={isSaving || !pipelineName.trim() || pipelineSteps.length === 0}
                  className="btn-windows-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSaving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4" />
                      <span>Save Pipeline</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success Message */}
      {showSuccess && (
        <div className="bg-green-50 border-b border-green-200 p-3">
          <div className="max-w-7xl mx-auto flex items-center space-x-2 text-green-700">
            <CheckCircle2 className="h-5 w-5" />
            <span className="font-medium">Pipeline saved successfully!</span>
          </div>
        </div>
      )}

      {/* Simple Header */}
      <div className="p-4 border-b border-windows-200 bg-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/')}
              className="btn-windows flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Home</span>
            </button>
            <h1 className="text-2xl font-bold text-windows-900">Create Task Pipeline</h1>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={clearPipeline}
              className="btn-windows"
            >
              Clear Pipeline
            </button>
          </div>
        </div>

        {/* Pipeline Name and Description */}
        {pipelineSteps.length > 0 && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-windows-700 mb-1">Pipeline Name *</label>
              <input
                type="text"
                value={pipelineName}
                onChange={(e) => setPipelineName(e.target.value)}
                placeholder="Enter pipeline name..."
                className="input-windows w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-windows-700 mb-1">Description</label>
              <input
                type="text"
                value={pipelineDescription}
                onChange={(e) => setPipelineDescription(e.target.value)}
                placeholder="Describe your pipeline..."
                className="input-windows w-full"
              />
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex min-h-0">
        {/* Left Pane - Task Selection */}
        <div className="w-80 bg-white border-r border-windows-200 p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold text-windows-900 mb-4 flex items-center space-x-2">
            <GitBranch className="h-5 w-5 text-accent-600" />
            <span>Available Tasks</span>
          </h2>
          
          <div className="space-y-3">
            {availableTasks.map((task) => (
              <div
                key={task.id}
                className="border border-windows-200 rounded-lg p-3 hover:border-accent-300 hover:shadow-sm transition-all cursor-pointer"
                onClick={() => addTaskToPipeline(task)}
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-accent-100 rounded-lg">
                    <task.icon className="h-5 w-5 text-accent-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-windows-900 text-sm">{task.name}</h3>
                    <p className="text-xs text-windows-600">{task.description}</p>
                    <span className="inline-block mt-1 px-2 py-1 bg-windows-100 text-windows-600 text-xs rounded">
                      {task.category}
                    </span>
                  </div>
                  <Plus className="h-4 w-4 text-accent-600" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Pane - Pipeline View */}
        <div className="flex-1 bg-windows-50 p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold text-windows-900 mb-4">Pipeline</h2>
          
          {pipelineSteps.length === 0 ? (
            <div className="text-center py-12">
              <GitBranch className="h-16 w-16 text-windows-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-windows-600 mb-2">No Tasks Added</h3>
              <p className="text-windows-500 text-sm">
                Click on tasks from the left panel to build your pipeline
              </p>
            </div>
          ) : (
            <div className="flex items-center space-x-4 overflow-x-auto pb-4">
              {pipelineSteps.map((step, index) => (
                <div key={step.id} className="flex items-center space-x-4">
                  {/* Task Node */}
                  <div className="flex flex-col items-center">
                    <div className="w-32 p-3 bg-white border-2 border-accent-400 rounded-lg shadow-sm text-center">
                      <div className="p-2 bg-accent-100 rounded-lg w-fit mx-auto mb-2">
                        <step.task.icon className="h-4 w-4 text-accent-600" />
                      </div>
                      <h4 className="font-medium text-windows-900 text-xs mb-1">{step.task.name}</h4>
                      <span className="text-xs text-accent-600">Step {index + 1}</span>
                    </div>
                    <button
                      onClick={() => removeTaskFromPipeline(step.id)}
                      className="mt-2 px-2 py-1 bg-red-100 hover:bg-red-200 text-red-600 text-xs rounded transition-colors"
                    >
                      <Trash2 className="h-3 w-3 inline mr-1" />
                      Remove
                    </button>
                  </div>
                  
                  {/* Connector Arrow */}
                  {index < pipelineSteps.length - 1 && (
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-0.5 bg-accent-400"></div>
                      <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-accent-400 transform rotate-90"></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Saved Pipelines Section */}
      {savedPipelines.length > 0 && (
        <div className="mt-6 p-4 bg-windows-50 border-t border-windows-200">
          <h3 className="text-lg font-semibold text-windows-900 mb-4">Saved Pipelines</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {savedPipelines.map((pipeline) => (
              <div key={pipeline.id} className="bg-white border border-windows-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-windows-900">{pipeline.name}</h4>
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                    {pipeline.status}
                  </span>
                </div>
                <p className="text-sm text-windows-600 mb-3">{pipeline.description}</p>
                <div className="flex items-center justify-between text-xs text-windows-500">
                  <span>{pipeline.steps.length} steps</span>
                  <span>{new Date(pipeline.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pipeline Diagram */}
      {/* <div className="mt-6">
        <PipelineDiagram />
      </div> */}
    </div>
  );
};

export default CreateTaskPipelinePage;
