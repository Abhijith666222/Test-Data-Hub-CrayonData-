import React from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { 
  Home, 
  Database, 
  FileText, 
  Settings, 
  BarChart3, 
  Play,
  Info,
  Menu,
  X,
  GitBranch
} from 'lucide-react';
import { useApp } from '../context/AppContext';

const Layout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { state } = useApp();
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const navigation = [
    { name: 'Product Overview', href: '/overview', icon: Info },
    { name: 'Create Test Scenarios', href: '/create', icon: Play },
    { name: 'Create Task Pipeline', href: '/create-pipeline', icon: GitBranch },
    { name: 'Data Workspace', href: '/', icon: Home },

  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="h-screen flex bg-windows-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white border-r border-windows-200 transition-all duration-300 ease-in-out`}>
        <div className="flex items-center justify-between p-4 border-b border-windows-200">
          <div className={`${sidebarOpen ? 'block' : 'hidden'} font-semibold text-lg text-windows-900`}>
            Test Data Hub
          </div>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-md hover:bg-windows-100 transition-colors duration-200"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className="mt-4">
          <div className="px-4 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.name}
                  onClick={() => navigate(item.href)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                    isActive(item.href)
                      ? 'text-accent-600 bg-accent-50'
                      : 'text-windows-700 hover:text-accent-600 hover:bg-accent-50'
                  }`}
                >
                  <Icon size={20} className="mr-3" />
                  {sidebarOpen && <span>{item.name}</span>}
                </button>
              );
            })}
          </div>

          {/* Recent Runs */}
          {sidebarOpen && state.runs.length > 0 && (
            <div className="mt-8 px-4">
              <h3 className="text-xs font-semibold text-windows-500 uppercase tracking-wider mb-3">
                Recent Runs
              </h3>
              <div className="space-y-1">
                {state.runs.slice(0, 5).map((run) => (
                  <button
                    key={run.run_id}
                    onClick={() => navigate(`/run/${run.run_id}`)}
                    className="w-full flex items-center px-3 py-2 text-sm text-windows-700 hover:text-accent-600 hover:bg-accent-50 rounded-md transition-colors duration-200"
                  >
                    <Database size={16} className="mr-2" />
                    <span className="truncate">Task {run.run_id}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Title Bar */}
        <div className="title-bar-windows">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-windows-900">
              {location.pathname === '/overview' && 'Product Overview'}
              {location.pathname === '/' && 'Home'}
              {location.pathname === '/create' && 'Create Data Tasks'}
              {location.pathname === '/create-pipeline' && 'Create Task Pipeline'}
              {location.pathname === '/data-source' && 'Connect Data Source'}
              {location.pathname === '/schema-analysis' && 'Schema Analysis'}
              {location.pathname === '/data-generation' && 'Data Generation'}
              {location.pathname === '/destination' && 'Destination System'}
              {location.pathname.startsWith('/run/') && `Run ${location.pathname.split('/')[2]}`}
            </h1>
          </div>
          
          <div className="flex items-center space-x-2">
            {state.isLoading && (
              <div className="flex items-center space-x-2 text-windows-600">
                <div className="spinner-windows w-4 h-4"></div>
                <span className="text-sm">Processing...</span>
              </div>
            )}
          </div>
        </div>

        {/* Content Area */}
        <div className="content-area-windows flex-1 overflow-auto">
          <Outlet />
        </div>

        {/* Status Bar */}
        <div className="status-bar-windows">
          <div className="flex items-center space-x-4">
            <span className="text-sm text-windows-600">
              {state.runs.length} runs available
            </span>
            {state.currentRun && (
              <span className="text-sm text-windows-600">
                Current: Run {state.currentRun.run_id}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-windows-600">
              {state.logs.length} log entries
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Layout; 