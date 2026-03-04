import React, { useCallback, useState } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap, 
  Node, 
  Edge,
  Handle,
  Position,
  NodeProps,
  applyNodeChanges,
  applyEdgeChanges
} from 'reactflow';
import { 
  Database, 
  Server, 
  FileText, 
  ChevronRight,
  ArrowRight,
  RefreshCw,
  Save
} from 'lucide-react';
import 'reactflow/dist/style.css';

// Node & Edge Definition
const PIPELINE_VERSION = '1.1'; // Version for cache invalidation

const nodes: Node[] = [
  { 
    id: 'prime', 
    position: { x: 50, y: 50 }, 
    data: { 
      label: 'Prime API', 
      type: 'system',
      description: 'Source system for credit card data',
      icon: 'Server'
    }, 
    type: 'pipelineNode' 
  },
  { 
    id: 'run1', 
    position: { x: 250, y: 50 }, 
    data: { 
      label: 'Task 1\nCollect Credit Cards', 
      type: 'process',
      description: 'Collect and process credit card data from Prime system'
    }, 
    type: 'pipelineNode' 
  },
  { 
    id: 'db1', 
    position: { x: 250, y: 200 }, 
    data: { 
      label: 'Workspace DB', 
      type: 'db',
      description: 'Save in Workspace DB',
      icon: 'Database'
    }, 
    type: 'pipelineNode' 
  },
  
  { 
    id: 'local', 
    position: { x: 450, y: -50 }, 
    data: { 
      label: 'Local', 
      type: 'system',
      description: 'Local data source for additional inputs',
      icon: 'FileText'
    }, 
    type: 'pipelineNode' 
  },
  { 
    id: 'run2', 
    position: { x: 450, y: 50 }, 
    data: { 
      label: 'Task 2\nGenerate Synthetic Data', 
      type: 'process',
      description: 'Generate synthetic data and continue modifying Workspace DB'
    }, 
    type: 'pipelineNode' 
  },
  { 
    id: 'db2', 
    position: { x: 450, y: 200 }, 
    data: { 
      label: 'Workspace DB', 
      type: 'db',
      description: 'Continue modifying Workspace DB',
      icon: 'Database'
    }, 
    type: 'pipelineNode' 
  },

  { 
    id: 'run3', 
    position: { x: 650, y: 50 }, 
    data: { 
      label: 'Task 3\nAdd Functional Test Scenarios', 
      type: 'process',
      description: 'Add functional test scenarios and continue modifying Workspace DB'
    }, 
    type: 'pipelineNode' 
  },
  { 
    id: 'db3', 
    position: { x: 650, y: 200 }, 
    data: { 
      label: 'Workspace DB', 
      type: 'db',
      description: 'Continue modifying Workspace DB',
      icon: 'Database'
    }, 
    type: 'pipelineNode' 
  },

  { 
    id: 'run4', 
    position: { x: 850, y: 50 }, 
    data: { 
      label: 'Task 4\nLoad Workspace DB & Push', 
      type: 'process',
      description: 'Load from Workspace DB and push to multiple destination servers'
    }, 
    type: 'pipelineNode' 
  },

  { 
    id: 'oracle', 
    position: { x: 1050, y: -50 }, 
    data: { 
      label: 'Oracle', 
      type: 'system',
      description: 'Oracle database destination',
      icon: 'Server'
    }, 
    type: 'pipelineNode' 
  },
  { 
    id: 'mysql', 
    position: { x: 1050, y: 150 }, 
    data: { 
      label: 'MySQL', 
      type: 'system',
      description: 'MySQL database destination',
      icon: 'Server'
    }, 
    type: 'pipelineNode' 
  }
];

const edges: Edge[] = [
  { 
    id: 'e1', 
    source: 'prime', 
    target: 'run1', 
    type: 'smoothstep',
    style: { stroke: '#3b82f6', strokeWidth: 2 }
  },
  { 
    id: 'e2', 
    source: 'run1', 
    target: 'db1', 
    type: 'smoothstep', 
    style: { stroke: '#f59e0b', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  { 
    id: 'e3', 
    source: 'run1', 
    target: 'run2', 
    type: 'smoothstep',
    style: { stroke: '#3b82f6', strokeWidth: 2 }
  },
  { 
    id: 'e4', 
    source: 'local', 
    target: 'run2', 
    type: 'smoothstep',
    style: { stroke: '#3b82f6', strokeWidth: 2 }
  },
  { 
    id: 'e5', 
    source: 'run2', 
    target: 'db2', 
    type: 'smoothstep', 
    style: { stroke: '#f59e0b', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  { 
    id: 'e6', 
    source: 'run2', 
    target: 'run3', 
    type: 'smoothstep',
    style: { stroke: '#3b82f6', strokeWidth: 2 }
  },
  { 
    id: 'e7', 
    source: 'run3', 
    target: 'db3', 
    type: 'smoothstep', 
    style: { stroke: '#f59e0b', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  { 
    id: 'e8', 
    source: 'run3', 
    target: 'run4', 
    type: 'smoothstep',
    style: { stroke: '#3b82f6', strokeWidth: 2 }
  },
  { 
    id: 'e9', 
    source: 'run4', 
    target: 'oracle', 
    type: 'smoothstep',
    style: { stroke: '#3b82f6', strokeWidth: 2 }
  },
  { 
    id: 'e10', 
    source: 'run4', 
    target: 'mysql', 
    type: 'smoothstep',
    style: { stroke: '#3b82f6', strokeWidth: 2 }
  },
  { 
    id: 'e11', 
    source: 'oracle', 
    target: 'mysql', 
    type: 'smoothstep', 
    style: { stroke: '#94a3b8', strokeWidth: 1, strokeDasharray: '3,3' }
  }
];

const PipelineNode: React.FC<NodeProps> = ({ data }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  
  // Handle icon properly - it might be a string from localStorage or a component
  const getIcon = () => {
    if (typeof data.icon === 'string') {
      // Map string names back to components
      switch (data.icon) {
        case 'Server':
          return Server;
        case 'Database':
          return Database;
        case 'FileText':
          return FileText;
        default:
          return null;
      }
    }
    return data.icon;
  };
  
  const Icon = getIcon();

  const getNodeStyles = () => {
    const baseClasses = "p-4 text-center rounded-lg shadow-windows transition-all duration-200 border-2 min-w-[120px] relative";
    
    switch (data.type) {
      case 'system':
        return `${baseClasses} bg-white border-accent-300 hover:border-accent-400 hover:shadow-windows-lg`;
      case 'process':
        return `${baseClasses} bg-accent-50 border-accent-400 hover:border-accent-500 hover:shadow-windows-lg`;
      case 'db':
        return `${baseClasses} bg-warning-50 border-warning-300 hover:border-warning-400 hover:shadow-windows-lg`;
      default:
        return `${baseClasses} bg-white border-windows-300`;
    }
  };

  const getIconColor = () => {
    switch (data.type) {
      case 'system':
        return 'text-accent-600';
      case 'process':
        return 'text-accent-700';
      case 'db':
        return 'text-warning-600';
      default:
        return 'text-windows-600';
    }
  };

  return (
    <div 
      className={getNodeStyles()}
      onMouseEnter={() => {
        console.log('Hovering over node:', data.label, 'Description:', data.description);
        setShowTooltip(true);
      }}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Input Handle - Left side */}
      <Handle 
        type="target" 
        position={Position.Left} 
        className="w-3 h-3 bg-accent-600 border-2 border-white"
        style={{ left: '-6px' }}
      />
      
      <div className="flex flex-col items-center space-y-2">
        {Icon && typeof Icon === 'function' && (
          <div className={`p-2 rounded-lg bg-white shadow-sm ${getIconColor()}`}>
            <Icon size={20} />
          </div>
        )}
        
        <div className="text-sm font-medium text-windows-900 whitespace-pre-line">
          {data.label}
        </div>
        
        {data.type === 'process' && (
          <div className="flex items-center space-x-1 text-xs text-accent-600">
            <ChevronRight size={12} />
            <span>Process</span>
          </div>
        )}
      </div>

      {/* Output Handle - Right side */}
      <Handle 
        type="source" 
        position={Position.Right} 
        className="w-3 h-3 bg-accent-600 border-2 border-white"
        style={{ right: '-6px' }}
      />
      
      {/* Tooltip */}
      {showTooltip && data.description && (
        <div className="absolute z-50 px-3 py-2 text-xs text-white bg-windows-800 rounded-lg shadow-windows-lg -top-16 left-1/2 transform -translate-x-1/2 whitespace-nowrap pointer-events-none">
          {data.description}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-windows-800"></div>
        </div>
      )}
    </div>
  );
};

// Define nodeTypes outside the component to prevent recreation on every render
const nodeTypes = {
  pipelineNode: PipelineNode
};

const PipelineDiagram: React.FC = () => {
  const [showSavedMessage, setShowSavedMessage] = useState(false);
  
  // Load saved positions from localStorage or use default
  const loadSavedPositions = () => {
    const saved = localStorage.getItem('pipeline-positions');
    const savedVersion = localStorage.getItem('pipeline-version');
    
    // Clear cache if version doesn't match
    if (savedVersion !== PIPELINE_VERSION) {
      localStorage.removeItem('pipeline-positions');
      localStorage.removeItem('pipeline-version');
      return nodes;
    }
    
    if (saved) {
      try {
        const savedNodes = JSON.parse(saved);
        // Ensure saved nodes have correct labels and descriptions by merging with original nodes
        const nodesWithDescriptions = savedNodes.map((savedNode: any) => {
          const originalNode = nodes.find(n => n.id === savedNode.id);
          return {
            ...savedNode,
            data: {
              ...originalNode?.data, // Use original data to ensure correct labels
              ...savedNode.data,     // Override with saved data for positions
              description: originalNode?.data.description || savedNode.data.description || 'No description available'
            }
          };
        });
        console.log('Loaded nodes with labels:', nodesWithDescriptions.map((node: Node) => ({ id: node.id, label: node.data.label })));
        return nodesWithDescriptions;
      } catch (error) {
        console.log('Failed to load saved positions, using defaults');
        return nodes;
      }
    }
    return nodes;
  };

  const [nodesState, setNodesState] = useState(loadSavedPositions);
  const [edgesState, setEdgesState] = useState(edges);

  // Debug: Log current node labels
  React.useEffect(() => {
    console.log('Current node labels:', nodesState.map((node: Node) => ({ id: node.id, label: node.data.label })));
    console.log('Expected labels:', nodes.map((node: Node) => ({ id: node.id, label: node.data.label })));
  }, [nodesState]);

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    console.log('Node clicked:', node);
  }, []);

  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    console.log('Edge clicked:', edge);
  }, []);

  const onNodesChange = useCallback((changes: any) => {
    setNodesState((currentNodes: Node[]) => {
      const updatedNodes = applyNodeChanges(changes, currentNodes);
      
      // Ensure correct labels are preserved when saving
      const nodesWithCorrectLabels = updatedNodes.map((updatedNode: Node) => {
        const originalNode = nodes.find(n => n.id === updatedNode.id);
        return {
          ...updatedNode,
          data: {
            ...originalNode?.data, // Use original data to ensure correct labels
            ...updatedNode.data,   // Override with updated data for positions
          }
        };
      });
      
      // Save positions to localStorage with version
      localStorage.setItem('pipeline-positions', JSON.stringify(nodesWithCorrectLabels));
      localStorage.setItem('pipeline-version', PIPELINE_VERSION);
      return nodesWithCorrectLabels;
    });
  }, []);

  const onEdgesChange = useCallback((changes: any) => {
    setEdgesState((eds: Edge[]) => applyEdgeChanges(changes, eds));
  }, []);

  const resetLayout = useCallback(() => {
    setNodesState(nodes);
    setEdgesState(edges);
    localStorage.removeItem('pipeline-positions');
    localStorage.removeItem('pipeline-version');
  }, []);

  // Only clear cache if version doesn't match on component mount
  React.useEffect(() => {
    const savedVersion = localStorage.getItem('pipeline-version');
    if (savedVersion !== PIPELINE_VERSION) {
      localStorage.removeItem('pipeline-positions');
      localStorage.removeItem('pipeline-version');
      setNodesState(nodes);
    }
  }, []);

  const [message, setMessage] = useState('');

  const savePositions = useCallback(() => {
    // Ensure correct labels are preserved when manually saving
    const nodesWithCorrectLabels = nodesState.map((currentNode: Node) => {
      const originalNode = nodes.find(n => n.id === currentNode.id);
      return {
        ...currentNode,
        data: {
          ...originalNode?.data, // Use original data to ensure correct labels
          ...currentNode.data,   // Override with current data for positions
        }
      };
    });
    
    console.log('Saving nodes with labels:', nodesWithCorrectLabels.map((node: Node) => ({ id: node.id, label: node.data.label })));
    
    localStorage.setItem('pipeline-positions', JSON.stringify(nodesWithCorrectLabels));
    localStorage.setItem('pipeline-version', PIPELINE_VERSION);
    setMessage('Positions saved!');
    setShowSavedMessage(true);
    setTimeout(() => setShowSavedMessage(false), 2000);
  }, [nodesState]);

  const clearSavedPositions = useCallback(() => {
    localStorage.removeItem('pipeline-positions');
    localStorage.removeItem('pipeline-version');
    setNodesState(nodes);
    setMessage('Saved positions cleared!');
    setShowSavedMessage(true);
    setTimeout(() => setShowSavedMessage(false), 2000);
  }, []);

  return (
    <div className="card-windows">
      <div className="p-6 border-b border-windows-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-windows-900 flex items-center space-x-2">
              <ArrowRight className="h-5 w-5 text-accent-600" />
              <span>Test Data Pipeline</span>
            </h2>
            <p className="text-windows-600 mt-1">
              Visual representation of the complete test data generation and deployment pipeline
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={savePositions}
              className="px-3 py-2 text-sm bg-accent-100 hover:bg-accent-200 text-accent-700 rounded-lg border border-accent-300 transition-colors duration-200 flex items-center space-x-2"
            >
              <Save className="h-4 w-4" />
              <span>Save Positions</span>
            </button>
            <button
              onClick={resetLayout}
              className="px-3 py-2 text-sm bg-windows-100 hover:bg-windows-200 text-windows-700 rounded-lg border border-windows-300 transition-colors duration-200 flex items-center space-x-2"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Reset Layout</span>
            </button>
            <button
              onClick={clearSavedPositions}
              className="px-3 py-2 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded-lg border border-red-300 transition-colors duration-200 flex items-center space-x-2"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Clear Cache</span>
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-6">
        <div className="h-[600px] w-full bg-windows-50 rounded-lg border border-windows-200 overflow-hidden relative">
          {/* Instructions Overlay */}
          <div className="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur-sm border border-windows-200 rounded-lg p-3 shadow-windows">
            <div className="text-xs text-windows-700 space-y-1">
              <div className="font-medium">💡 Interactive Diagram</div>
              <div>• Drag nodes to reposition</div>
              <div>• Positions auto-save as you move</div>
              <div>• Scroll to zoom in/out</div>
              <div>• Hover for tooltips</div>
            </div>
          </div>

          {/* Saved Message */}
          {showSavedMessage && (
            <div className="absolute top-4 right-4 z-10 bg-success-100 border border-success-300 text-success-700 px-3 py-2 rounded-lg shadow-windows animate-slide-in">
              <div className="flex items-center space-x-2 text-sm">
                <Save className="h-4 w-4" />
                <span>Positions saved!</span>
              </div>
            </div>
          )}
          <ReactFlow
            key={`pipeline-${PIPELINE_VERSION}`}
            nodes={nodesState}
            edges={edgesState}
            nodeTypes={nodeTypes}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            fitViewOptions={{ padding: 0.3 }}
            defaultEdgeOptions={{
              type: 'smoothstep',
              style: { stroke: '#3b82f6', strokeWidth: 2 }
            }}
            snapToGrid={true}
            snapGrid={[15, 15]}
            proOptions={{ hideAttribution: true }}
            nodesDraggable={true}
            nodesConnectable={false}
            elementsSelectable={true}
          >
            <Background 
              color="#e2e8f0" 
              gap={20} 
              size={1}
            />
            <Controls 
              className="bg-white border border-windows-200 rounded-lg shadow-windows"
            />
            <MiniMap 
              className="bg-white border border-windows-200 rounded-lg shadow-windows"
              nodeColor="#3b82f6"
              maskColor="rgba(0, 0, 0, 0.1)"
            />
          </ReactFlow>
        </div>
        
        {/* Legend */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-white border-2 border-accent-300 rounded"></div>
            <span className="text-windows-700">System Nodes</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-accent-50 border-2 border-accent-400 rounded"></div>
            <span className="text-windows-700">Task Nodes</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-warning-50 border-2 border-warning-300 rounded"></div>
            <span className="text-windows-700">Database Nodes</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-0.5 bg-accent-600"></div>
            <span className="text-windows-700">Data Flow</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-0.5 bg-accent-600 border-dashed border-accent-600"></div>
            <span className="text-windows-700">Storage</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PipelineDiagram; 