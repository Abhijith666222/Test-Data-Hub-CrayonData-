import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Database, 
  FileText, 
  Shield, 
  BarChart3,
  CheckCircle,
  ArrowRight,
  Sparkles,
  Zap,
  Lock,
  TrendingUp
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { ProductType } from '../context/AppContext';

const CreateSystemPage: React.FC = () => {
  const navigate = useNavigate();
  const { dispatch } = useApp();

  const productTypes: ProductType[] = [
    {
      id: 'synthetic-data-generation',
      name: 'Generate Sythetic Data',
      description: 'Create realistic synthetic data for testing and development with advanced data patterns and referential integrity.',
      icon: 'BarChart3',
      available: true,
      features: [
        'Realistic data patterns',
        'Referential integrity',
        'Multiple output formats'
      ]
    },
    {
      id: 'functional-test-scenarios',
      name: 'Add Test Data Scenarios',
      description: 'Generate comprehensive test scenarios for functional testing with AI-powered analysis and business rule validation.',
      icon: 'Database',
      available: true,
      features: [
        'AI-powered test scenario analysis',
        'Comprehensive test coverage',
        'Integration with existing test frameworks'
      ]
    },
    {
      id: 'data-masking',
      name: 'Perform Data Masking & Anonymization',
      description: 'Protect sensitive data with advanced masking techniques while maintaining data utility for testing.',
      icon: 'Shield',
      available: false,
      features: [
        'Advanced masking algorithms',
        'Compliance reporting',

      ]
    },
    {
      id: 'data-enrichment',
      name: 'Perform Data Enrichment & Enhancement',
      description: 'Enhance existing datasets with additional attributes and relationships for comprehensive testing.',
      icon: 'TrendingUp',
      available: false,
      features: [
        'Intelligent data augmentation',
        'Custom enrichment rules'
      ]
    }
  ];

  const handleProductSelect = (product: ProductType) => {
    if (!product.available) {
      return; // Don't allow selection of unavailable products
    }
    
    dispatch({ type: 'SET_SELECTED_PRODUCT', payload: product });
    navigate('/data-source');
  };

  const getProductIcon = (iconName: string) => {
    switch (iconName) {
      case 'Database':
        return <Database className="h-8 w-8" />;
      case 'BarChart3':
        return <BarChart3 className="h-8 w-8" />;
      case 'Shield':
        return <Shield className="h-8 w-8" />;
      case 'TrendingUp':
        return <TrendingUp className="h-8 w-8" />;
      default:
        return <Database className="h-8 w-8" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-windows-900">Create Test Data & Scenarios</h1>
        <p className="text-windows-600 mt-2 max-w-2xl mx-auto">
          Choose the type of data generation system you want to create. Each data solution line offers specialized capabilities for different testing and development needs.
        </p>
      </div>

      {/* Product Selection Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {productTypes.map((product) => (
          <div
            key={product.id}
            className={`card-windows p-6 transition-all duration-200 ${
              product.available
                ? 'hover:shadow-windows-lg cursor-pointer hover:scale-[1.02]'
                : 'opacity-60 cursor-not-allowed'
            }`}
            onClick={() => handleProductSelect(product)}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`p-3 rounded-lg ${
                  product.available 
                    ? 'bg-accent-100 text-accent-600' 
                    : 'bg-windows-100 text-windows-400'
                }`}>
                  {getProductIcon(product.icon)}
                </div>
                <div>
                  <h3 className="font-semibold text-windows-900 text-lg">{product.name}</h3>
                  {!product.available && (
                    <span className="badge-windows badge-windows-warning text-xs">
                      Coming Soon
                    </span>
                  )}
                </div>
              </div>
              {product.available && (
                <ArrowRight className="h-5 w-5 text-windows-400" />
              )}
            </div>

            <p className="text-windows-600 mb-6 leading-relaxed">
              {product.description}
            </p>

            <div className="space-y-3">
              <h4 className="font-medium text-windows-900 flex items-center space-x-2">
                <Sparkles className="h-4 w-4 text-accent-600" />
                <span>Key Features</span>
              </h4>
              <ul className="space-y-2">
                {product.features.map((feature, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-success-600 mt-0.5 flex-shrink-0" />
                    <span className="text-windows-700">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            {product.available && (
              <div className="mt-6 pt-4 border-t border-windows-100">
                <button className="btn-windows-primary w-full flex items-center justify-center space-x-2">
                  <span>Select {product.name}</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            )}

            {!product.available && (
              <div className="mt-6 pt-4 border-t border-windows-100">
                <div className="flex items-center justify-center space-x-2 text-windows-500">
                  <Lock className="h-4 w-4" />
                  <span className="text-sm">Available in future releases</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Additional Information */}
      <div className="card-windows">
        <div className="p-6 border-b border-windows-200">
          <h2 className="text-xl font-semibold text-windows-900">Why Choose Our Test Data Workspace?</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="p-3 bg-success-100 rounded-lg w-fit mx-auto mb-3">
                <Zap className="h-6 w-6 text-success-600" />
              </div>
              <h3 className="font-semibold text-windows-900 mb-2">AI-Powered</h3>
              <p className="text-windows-600 text-sm">
                Advanced AI algorithms analyze your data and generate intelligent test scenarios and synthetic data.
              </p>
            </div>
            
            <div className="text-center">
              <div className="p-3 bg-info-100 rounded-lg w-fit mx-auto mb-3">
                <Shield className="h-6 w-6 text-info-600" />
              </div>
              <h3 className="font-semibold text-windows-900 mb-2">Secure & Compliant</h3>
              <p className="text-windows-600 text-sm">
                Built with security and compliance in mind, ensuring your data remains protected throughout the process.
              </p>
            </div>
            
            <div className="text-center">
              <div className="p-3 bg-warning-100 rounded-lg w-fit mx-auto mb-3">
                <BarChart3 className="h-6 w-6 text-warning-600" />
              </div>
              <h3 className="font-semibold text-windows-900 mb-2">Comprehensive</h3>
              <p className="text-windows-600 text-sm">
                Complete solution covering schema analysis, data generation, validation, and integration capabilities.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Back Button */}
      <div className="flex justify-center">
        <button
          onClick={() => navigate('/')}
          className="btn-windows flex items-center space-x-2"
        >
          <span>Back to Home</span>
        </button>
      </div>
    </div>
  );
};

export default CreateSystemPage;

export {}; 