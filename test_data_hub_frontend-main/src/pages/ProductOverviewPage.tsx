import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Database, 
  FileText, 
  Shield, 
  BarChart3,
  Zap,
  CheckCircle,
  ArrowRight,
  Play,
  Sparkles,
  Globe,
  Server,
  TrendingUp,
  Lock,
  Users,
  Settings
} from 'lucide-react';

const ProductOverviewPage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: BarChart3,
      title: 'AI Powered Synthetic Data Generation',
      description: 'Generate realistic test data that maintains referential integrity and follows your business rules.',
      benefits: ['Realistic data patterns', 'Referential integrity']
    },
    {
      icon: FileText,
      title: 'Test Scenario Management',
      description: 'Create and manage comprehensive test scenarios with natural language processing capabilities.',
      benefits: ['Natural language input', 'Scenario templates']
    },
    {
      icon: Database,
      title: 'AI-Powered Schema Analysis',
      description: 'Advanced AI algorithms analyze your data structure, identify patterns, relationships, and business rules automatically.',
      benefits: ['Automatic pattern detection', 'Relationship mapping']
    },

    {
      icon: Shield,
      title: 'Data Validation & Quality',
      description: 'Comprehensive validation ensures your generated data meets quality standards and business requirements.',
      benefits: ['Automated validation', 'Compliance checking']
    }
  ];

  const productLines = [
    {
      id: 'synthetic-data-generation',
      name: 'Generate Sythetic Data',
      icon: BarChart3,
      description: 'Create realistic synthetic data for testing and development with advanced patterns.',
      status: 'Available',
      statusColor: 'success'
    },
    {
      id: 'functional-test-scenarios',
      name: 'Add Test Data Scenarios',
      icon: FileText,
      description: 'Generate comprehensive test scenarios for functional testing with AI-powered analysis.',
      status: 'Available',
      statusColor: 'success'
    },
    {
      id: 'data-masking',
      name: 'Perform Data Masking & Anonymization',
      icon: Lock,
      description: 'Protect sensitive data with advanced masking techniques while maintaining utility.',
      status: 'Coming Soon',
      statusColor: 'warning'
    },
    {
      id: 'data-enrichment',
      name: 'Perform Data Enrichment & Enhancement',
      icon: TrendingUp,
      description: 'Enhance existing datasets with additional attributes and relationships.',
      status: 'Coming Soon',
      statusColor: 'warning'
    }
  ];

  const useCases = [
    {
      title: 'Software Testing',
      description: 'Generate comprehensive test data for unit, integration, and system testing.',
      icon: Play
    },
    {
      title: 'Development Environments',
      description: 'Create realistic development databases with proper data relationships.',
      icon: Settings
    },
    {
      title: 'Data Analytics',
      description: 'Generate sample datasets for analytics and reporting development.',
      icon: BarChart3
    },
    {
      title: 'Training & Demos',
      description: 'Create training datasets for user acceptance testing and demonstrations.',
      icon: Users
    }
  ];

  const getStatusBadge = (status: string, color: string) => {
    return (
      <span className={`badge-windows badge-windows-${color}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-windows-900 mb-4">
          Test Data Hub
        </h1>
        <p className="text-xl text-windows-600 max-w-3xl mx-auto mb-8">
          AI-powered synthetic data generation and validation system for comprehensive testing and development workflows.
        </p>
        <div className="flex items-center justify-center space-x-4">
          <button
            onClick={() => navigate('/create')}
            className="btn-windows-primary flex items-center space-x-2 px-6 py-3"
          >
            <Play className="h-5 w-5" />
            <span>Get Started</span>
          </button>
          <button
            onClick={() => navigate('/')}
            className="btn-windows flex items-center space-x-2 px-6 py-3"
          >
            <span>View Existing Systems</span>
            <ArrowRight className="h-5 w-5" />
          </button>
        </div>
      </div>

             {/* Product Lines */}
       <div className="card-windows">
         <div className="p-6 border-b border-windows-200">
           <h2 className="text-2xl font-semibold text-windows-900">Data Solutions</h2>
           <p className="text-windows-600 mt-2">
             Choose the right solution for your specific testing and data generation needs.
           </p>
         </div>
         
         <div className="p-6">
           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             {productLines.map((product, index) => {
               const Icon = product.icon;
               return (
                 <div key={index} className="p-6 border border-windows-200 rounded-lg hover:shadow-windows-lg transition-all duration-200">
                   <div className="flex items-start justify-between mb-4">
                     <div className="flex items-center space-x-3">
                       <div className="p-3 bg-accent-100 rounded-lg">
                         <Icon className="h-6 w-6 text-accent-600" />
                       </div>
                       <div>
                         <h3 className="font-semibold text-windows-900">{product.name}</h3>
                         {getStatusBadge(product.status, product.statusColor)}
                       </div>
                     </div>
                   </div>
                   <p className="text-windows-600 mb-4">{product.description}</p>
                   {product.status === 'Available' && (
                     <button
                       onClick={() => navigate('/create')}
                       className="btn-windows-primary flex items-center space-x-2"
                     >
                       <span>Try Now</span>
                       <ArrowRight className="h-4 w-4" />
                     </button>
                   )}
                 </div>
               );
             })}
           </div>
         </div>
       </div>

       {/* Workspace Integration */}
       <div className="card-windows">
         <div className="p-6 border-b border-windows-200">
           <h2 className="text-2xl font-semibold text-windows-900 flex items-center space-x-2">
             <Server className="h-6 w-6 text-accent-600" />
             <span>Seamless Pipeline Integration</span>
           </h2>
           <p className="text-windows-600 mt-2">
             Connect to any of your data systems and pipelines seamlessly. Get data from your sources and push generated data back to your pipeline.
           </p>
         </div>
         
         <div className="p-6">
           <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
             {/* Connect to Data Sources */}
             <div className="text-center">
               <div className="p-4 bg-accent-100 rounded-lg w-fit mx-auto mb-4">
                 <Database className="h-8 w-8 text-accent-600" />
               </div>
               <h3 className="font-semibold text-windows-900 mb-3">Connect to Data Sources</h3>
               <div className="space-y-2 text-sm text-windows-600">
                 <div>SQL Databases (MySQL, PostgreSQL, Oracle)</div>
                 <div>Cloud Storage (AWS S3, Azure Blob)</div>
                 <div>REST APIs & Web Services</div>
               </div>
             </div>
             
             {/* Processing Engine */}
             <div className="text-center">
               <div className="p-4 bg-accent-100 rounded-lg w-fit mx-auto mb-4">
                 <Zap className="h-8 w-8 text-accent-600" />
               </div>
               <h3 className="font-semibold text-windows-900 mb-3">Generate Test Data with AI</h3>
               <div className="space-y-2 text-sm text-windows-600">
                 <div>Schema Analysis & Discovery</div>
                 <div>Business Rule Extraction</div>
                 <div>Synthetic Data Generation</div>
               </div>
             </div>
             
             {/* Destination Systems */}
             <div className="text-center">
               <div className="p-4 bg-accent-100 rounded-lg w-fit mx-auto mb-4">
                 <Globe className="h-8 w-8 text-accent-600" />
               </div>
               <h3 className="font-semibold text-windows-900 mb-3">Push to Destination Systems</h3>
               <div className="space-y-2 text-sm text-windows-600">
                 <div>Database Systems & Warehouses</div>
                 <div>API Endpoints</div>
                 <div>File Exports</div>
               </div>
             </div>
           </div>
           
           {/* Integration Flow Visualization */}
           <div className="mt-8 p-6 bg-gradient-to-r from-accent-50 to-accent-100 rounded-lg">
             <div className="flex items-center justify-center space-x-4">
               <div className="flex items-center space-x-2">
                 <div className="p-2 bg-white rounded-full shadow-sm">
                   <Database className="h-5 w-5 text-accent-600" />
                 </div>
                 <span className="text-sm font-medium text-windows-700">Source Data Sources</span>
               </div>
               <ArrowRight className="h-5 w-5 text-accent-600" />
               <div className="flex items-center space-x-2">
                 <div className="p-2 bg-white rounded-full shadow-sm">
                   <Zap className="h-5 w-5 text-accent-600" />
                 </div>
                 <span className="text-sm font-medium text-windows-700">AI Processing</span>
               </div>
               <ArrowRight className="h-5 w-5 text-accent-600" />
               <div className="flex items-center space-x-2">
                 <div className="p-2 bg-white rounded-full shadow-sm">
                   <Globe className="h-5 w-5 text-accent-600" />
                 </div>
                 <span className="text-sm font-medium text-windows-700">Destination Systems</span>
               </div>
             </div>
             <p className="text-center text-sm text-windows-600 mt-4">
               Seamless integration with your existing data pipeline and workflows
             </p>
           </div>
         </div>
       </div>

      {/* Key Features */}
      <div className="card-windows">
        <div className="p-6 border-b border-windows-200">
          <h2 className="text-2xl font-semibold text-windows-900 flex items-center space-x-2">
            <Sparkles className="h-6 w-6 text-accent-600" />
            <span>Key Features</span>
          </h2>
          <p className="text-windows-600 mt-2">
            Discover what makes Test Data Environment the ultimate solution for your data generation needs.
          </p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="p-6 border border-windows-200 rounded-lg hover:shadow-windows-lg transition-all duration-200">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-accent-100 rounded-lg">
                      <Icon className="h-6 w-6 text-accent-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-windows-900 mb-2">{feature.title}</h3>
                      <p className="text-windows-600 mb-4">{feature.description}</p>
                      <ul className="space-y-1">
                        {feature.benefits.map((benefit, benefitIndex) => (
                          <li key={benefitIndex} className="flex items-center space-x-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-success-600" />
                            <span className="text-windows-700">{benefit}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Use Cases */}
      <div className="card-windows">
        <div className="p-6 border-b border-windows-200">
          <h2 className="text-2xl font-semibold text-windows-900">Use Cases</h2>
          <p className="text-windows-600 mt-2">
            Perfect for various scenarios in software development and testing.
          </p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {useCases.map((useCase, index) => {
              const Icon = useCase.icon;
              return (
                <div key={index} className="text-center p-6 border border-windows-200 rounded-lg hover:shadow-windows-lg transition-all duration-200">
                  <div className="p-3 bg-accent-100 rounded-lg w-fit mx-auto mb-4">
                    <Icon className="h-6 w-6 text-accent-600" />
                  </div>
                  <h3 className="font-semibold text-windows-900 mb-2">{useCase.title}</h3>
                  <p className="text-windows-600 text-sm">{useCase.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>



      {/* Call to Action */}
      <div className="card-windows bg-gradient-to-r from-accent-600 to-accent-700 text-white">
        <div className="p-8 text-center">
          <h2 className="text-2xl font-semibold mb-4">Ready to Get Started?</h2>
          <p className="text-accent-100 mb-6 max-w-2xl mx-auto">
            Join thousands of developers who trust Test Data Environment for their synthetic data generation needs.
          </p>
          <div className="flex items-center justify-center space-x-4">
            <button
              onClick={() => navigate('/create')}
              className="bg-white text-accent-600 px-6 py-3 rounded-md font-medium hover:bg-accent-50 transition-colors duration-200 flex items-center space-x-2"
            >
              <Play className="h-5 w-5" />
              <span>Create Your First System</span>
            </button>
            <button
              onClick={() => navigate('/')}
              className="border border-white text-white px-6 py-3 rounded-md font-medium hover:bg-white hover:text-accent-600 transition-colors duration-200"
            >
              Explore Existing Systems
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductOverviewPage;

export {}; 