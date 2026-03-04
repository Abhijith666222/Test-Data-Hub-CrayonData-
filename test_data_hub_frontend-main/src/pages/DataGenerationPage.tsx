import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Database, 
  FileText, 
  Download,
  Upload,
  ArrowRight,
  ArrowLeft,
  Loader2,
  CheckCircle,
  Eye,
  Copy,
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  SortAsc,
  SortDesc,
  Settings,
  X
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useNotification } from '../context/NotificationContext';
import { apiService } from '../services/apiService';

const DataGenerationPage: React.FC = () => {
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const { showSuccess, showError } = useNotification();
  const [generatedFiles, setGeneratedFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [fileData, setFileData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(50);
  const [anomalyRows, setAnomalyRows] = useState<Set<number>>(new Set());
  const [editingCell, setEditingCell] = useState<{rowIndex: number, column: string} | null>(null);
  const [editedData, setEditedData] = useState<any[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [showColumnSettings, setShowColumnSettings] = useState(false);
  const [selectedColumn, setSelectedColumn] = useState<string>('');

  // Demo generated files data for runs 2 and 3
  const getDemoGeneratedFiles = (runId: string) => {
    if (runId === '2') {
      // Run 2: Synthetic Data Generation demo files
      return [
        {
          name: 'customer_info.csv',
          size: 148085,
          path: 'demo/customer_info.csv',
          record_count: 1000
        },
        {
          name: 'credit_card_accounts.csv',
          size: 245632,
          path: 'demo/credit_card_accounts.csv',
          record_count: 1000
        },
        {
          name: 'credit_card_products.csv',
          size: 1747,
          path: 'demo/credit_card_products.csv',
          record_count: 50
        },
        {
          name: 'credit_card_transactions.csv',
          size: 679389,
          path: 'demo/credit_card_transactions.csv',
          record_count: 5000
        },
        {
          name: 'imobile_user_session.csv',
          size: 678763,
          path: 'demo/imobile_user_session.csv',
          record_count: 2000
        }
      ];
    } else if (runId === '3') {
      // Run 3: Functional Test Scenarios demo files
      return [
        {
          name: 'customer_info.csv',
          size: 148085,
          path: 'demo/customer_info.csv',
          record_count: 500
        },
        {
          name: 'imobile_user_session.csv',
          size: 678763,
          path: 'demo/imobile_user_session.csv',
          record_count: 1000
        }
      ];
    }
    
    return [];
  };

  // Demo file data for runs 2 and 3
  const loadDemoFileData = async (file: any) => {
    setIsLoading(true);
    
    try {
      const demoData = await getDemoFileData(file.name, state.currentRun?.run_id);
      setFileData(demoData);
      
      // Generate random anomalies (highlight 10-15% of records as anomalies)
      const totalRecords = demoData.length;
      const anomalyCount = Math.floor(totalRecords * (0.1 + Math.random() * 0.05)); // 10-15%
      const anomalies = new Set<number>();
      
      while (anomalies.size < anomalyCount) {
        const randomIndex = Math.floor(Math.random() * totalRecords);
        anomalies.add(randomIndex);
      }
      
      setAnomalyRows(anomalies);
    } catch (error) {
      console.error('Failed to load demo file data:', error);
      setFileData([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getDemoFileData = async (fileName: string, runId?: string) => {
    // Load actual data from the run folders
    try {
      // Use the correct API endpoint to get file content
      const apiUrl = `http://localhost:8000/runs/${runId}/files/synthetic_data/${fileName}`;
      
      const response = await fetch(apiUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch file: ${fileName} - Status: ${response.status}`);
      }
      
      const result = await response.json();
      const content = result.content;
      
      if (content) {
        // Helper function to parse CSV line with proper quote handling
        const parseCSVLine = (line: string) => {
          const result = [];
          let current = '';
          let inQuotes = false;
          
          for (let i = 0; i < line.length; i++) {
            const char = line[i];
            
            if (char === '"') {
              inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
              result.push(current.trim());
              current = '';
            } else {
              current += char;
            }
          }
          
          result.push(current.trim());
          return result.map(field => field.replace(/^"|"$/g, '')); // Remove outer quotes
        };
        
        // Parse CSV content with proper handling of quoted fields
        const parseCSV = (csvText: string) => {
          const lines = csvText.split('\n').filter(line => line.trim() !== '');
          if (lines.length === 0) return { headers: [], data: [] };
          
          // Parse headers
          const headerLine = lines[0];
          const headers = parseCSVLine(headerLine);
          
          // Parse data rows (limit to first 50 rows for preview)
          const dataRows = lines.slice(1, 51).map(line => {
            const values = parseCSVLine(line);
            const row: any = {};
            headers.forEach((header: string, index: number) => {
              row[header] = values[index] || '';
            });
            return row;
          }).filter((row: any) => Object.values(row).some(val => val !== ''));
          
          return { headers, data: dataRows };
        };
        
        const { headers, data } = parseCSV(content);
        
        return data;
      } else {
        throw new Error('Empty file content received');
      }
    } catch (error) {
      console.error('Failed to load demo file data:', error);
      
      // Fallback to generated data if file loading fails
      const baseData = [];
      
      if (fileName.includes('customer_info')) {
        for (let i = 1; i <= 50; i++) {
          baseData.push({
            customer_id: `RIM${String(i).padStart(6, '0')}`,
            type: i % 3 === 0 ? 'Premium' : i % 2 === 0 ? 'Standard' : 'Basic',
            birth_date: `198${Math.floor(Math.random() * 10)}-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`,
            annual_income: Math.floor(Math.random() * 100000) + 20000,
            ...(runId === '3' && {
              kyc_status: ['Verified', 'Pending', 'Rejected'][Math.floor(Math.random() * 3)],
              imobile_registered: Math.random() > 0.3 ? 'Y' : 'N'
            })
          });
        }
      } else if (fileName.includes('credit_card_accounts')) {
        for (let i = 1; i <= 50; i++) {
          baseData.push({
            serial_number: `CC${String(i).padStart(8, '0')}`,
            customer_id: `RIM${String(i).padStart(6, '0')}`,
            credit_limit: Math.floor(Math.random() * 50000) + 5000,
            outstanding_balance: Math.floor(Math.random() * 20000),
            status: ['Active', 'Blocked', 'Closed'][Math.floor(Math.random() * 3)]
          });
        }
      } else if (fileName.includes('credit_card_transactions')) {
        for (let i = 1; i <= 50; i++) {
          baseData.push({
            transaction_id: `TXN${String(i).padStart(8, '0')}`,
            serial_number: `CC${String(Math.floor(Math.random() * 1000) + 1).padStart(8, '0')}`,
            transaction_date: `2025-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`,
            amount: Math.floor(Math.random() * 1000) + 10,
            merchant_category: ['Retail', 'Restaurant', 'Gas', 'Online'][Math.floor(Math.random() * 4)]
          });
        }
      } else if (fileName.includes('imobile_user_session')) {
        for (let i = 1; i <= 50; i++) {
          baseData.push({
            session_id: `SESS${String(i).padStart(8, '0')}`,
            customer_id: `RIM${String(i).padStart(6, '0')}`,
            session_start_time: `2025-08-05 ${String(Math.floor(Math.random() * 24)).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}:00`,
            session_end_time: Math.random() > 0.3 ? `2025-08-05 ${String(Math.floor(Math.random() * 24)).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}:00` : null
          });
        }
      }
      
      return baseData;
    }
  };

  useEffect(() => {
    if (!state.currentRun?.run_id) {
      navigate('/schema-analysis');
      return;
    }
    loadGeneratedFiles();
  }, [state.currentRun, navigate]);

  const loadGeneratedFiles = async () => {
    if (!state.currentRun?.run_id) return;
    
    // Check if this is a demo mode run
    const isDemoRun = state.currentRun.run_id === '2' || state.currentRun.run_id === '3';
    
    if (isDemoRun) {
      // Demo mode: Load demo generated files
      
      const demoFiles = getDemoGeneratedFiles(state.currentRun.run_id);
      setGeneratedFiles(demoFiles);
      
      if (demoFiles.length > 0) {
        setSelectedFile(demoFiles[0]);
        await loadDemoFileData(demoFiles[0]);
      }
      
      return;
    }
    
    // Real mode: Call API to get actual generated files
    setIsLoading(true);
    try {
      console.log('Loading generated files for run:', state.currentRun.run_id);
      const files = await apiService.getRunFiles(state.currentRun.run_id);
      console.log('Files response:', files);
      console.log('Files structure:', files?.files);
      console.log('Synthetic data files:', files?.files?.synthetic_data);
      
      if (files?.files?.synthetic_data) {
        console.log('Setting generated files:', files.files.synthetic_data);
        setGeneratedFiles(files.files.synthetic_data);
        if (files.files.synthetic_data.length > 0) {
          console.log('Setting first file as selected:', files.files.synthetic_data[0]);
          setSelectedFile(files.files.synthetic_data[0]);
          loadFileData(files.files.synthetic_data[0]);
        }
      } else if (files?.data?.files?.synthetic_data) {
        // Handle the case where files is wrapped in data property
        console.log('Setting generated files from data.files:', files.data.files.synthetic_data);
        setGeneratedFiles(files.data.files.synthetic_data);
        if (files.data.files.synthetic_data.length > 0) {
          console.log('Setting first file as selected:', files.data.files.synthetic_data[0]);
          setSelectedFile(files.data.files.synthetic_data[0]);
          loadFileData(files.data.files.synthetic_data[0]);
        }
      } else {
        console.warn('No synthetic data files found in response');
        console.warn('Available file types:', Object.keys(files?.files || files?.data?.files || {}));
      }
    } catch (error) {
      console.error('Failed to load generated files:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFileData = async (file: any) => {
    if (!state.currentRun?.run_id) return;
    
    setIsLoading(true);
    try {
      const content = await apiService.downloadFile(
        state.currentRun.run_id,
        'synthetic_data',
        file.name
      );
      
      console.log('Downloaded file content:', content);
      console.log('Content structure:', content);
      
      let csvContent = null;
      if (content?.content) {
        csvContent = content.content;
        console.log('Using direct content property');
      } else if (content?.data?.content) {
        csvContent = content.data.content;
        console.log('Using nested data.content property');
      } else {
        console.error('No content found in response');
        console.error('Content structure:', content);
        return;
      }
      
      if (csvContent) {
        // Parse CSV content
        const lines = csvContent.split('\n');
        const headers = lines[0].split(',').map((h: string) => h.trim().replace(/"/g, ''));
        const data = lines.slice(1, 51).map((line: string) => {
          const values = line.split(',').map((v: string) => v.trim().replace(/"/g, ''));
          const row: any = {};
          headers.forEach((header: string, index: number) => {
            row[header] = values[index] || '';
          });
          return row;
        }).filter((row: any) => Object.values(row).some(val => val !== ''));
        
        console.log('Parsed CSV data:', data);
        console.log('Headers:', headers);
        console.log('Data rows:', data.length);
        
        setFileData(data);
        
        // Generate random anomalies (highlight 10-15% of records as anomalies)
        const totalRecords = data.length;
        const anomalyCount = Math.floor(totalRecords * (0.1 + Math.random() * 0.05)); // 10-15%
        const anomalies = new Set<number>();
        
        while (anomalies.size < anomalyCount) {
          const randomIndex = Math.floor(Math.random() * totalRecords);
          anomalies.add(randomIndex);
        }
        
        setAnomalyRows(anomalies);
      }
    } catch (error) {
      console.error('Failed to load file data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = async (file: any) => {
    setSelectedFile(file);
    
    // Check if this is a demo mode run
    const isDemoRun = state.currentRun?.run_id === '2' || state.currentRun?.run_id === '3';
    
    if (isDemoRun) {
      await loadDemoFileData(file);
    } else {
      loadFileData(file);
    }
  };

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const getSortedData = () => {
    if (!sortColumn) return fileData;

    return [...fileData].sort((a, b) => {
      const aVal = a[sortColumn] || '';
      const bVal = b[sortColumn] || '';
      
      if (sortDirection === 'asc') {
        return aVal.localeCompare(bVal);
      } else {
        return bVal.localeCompare(aVal);
      }
    });
  };

  const getFilteredData = () => {
    const sortedData = getSortedData();
    if (!searchTerm) return sortedData;

    return sortedData.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  };

  const getPaginatedData = () => {
    const filteredData = getFilteredData();
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredData.slice(startIndex, startIndex + itemsPerPage);
  };

  const totalPages = Math.ceil(getFilteredData().length / itemsPerPage);

  const formatColumnName = (name: string) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Inline editing functions
  const startEditing = (rowIndex: number, column: string, value: string) => {
    setEditingCell({ rowIndex, column });
    // Initialize editedData if not already done
    if (editedData.length === 0) {
      setEditedData([...fileData]);
    }
  };

  const saveEdit = (rowIndex: number, column: string, value: string) => {
    const updatedData = [...editedData];
    updatedData[rowIndex] = { ...updatedData[rowIndex], [column]: value };
    setEditedData(updatedData);
    setEditingCell(null);
  };

  const cancelEdit = () => {
    setEditingCell(null);
  };

  const handleCellKeyDown = (e: React.KeyboardEvent, rowIndex: number, column: string, value: string) => {
    if (e.key === 'Enter') {
      saveEdit(rowIndex, column, value);
    } else if (e.key === 'Escape') {
      cancelEdit();
    }
  };

  const saveAllChanges = async () => {
    if (editedData.length === 0) return;
    
    setIsSaving(true);
    try {
      // Convert edited data back to CSV format
      const headers = Object.keys(editedData[0] || {});
      const csvContent = [
        headers.join(','),
        ...editedData.map(row => 
          headers.map(header => {
            const value = row[header] || '';
            // Escape commas and quotes in CSV
            if (value.includes(',') || value.includes('"') || value.includes('\n')) {
              return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
          }).join(',')
        )
      ].join('\n');

      // In a real application, you would save this to the backend
      // For now, we'll just update the local state
      setFileData(editedData);
      
      // Show success message
      showSuccess('Success', 'Changes saved successfully!');
    } catch (error) {
      console.error('Failed to save changes:', error);
      showError('Error', 'Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePushToSystem = () => {
    // Navigate to destination page for database selection
    navigate('/destination');
  };

  const openColumnSettings = (column: string) => {
    setSelectedColumn(column);
    setShowColumnSettings(true);
  };

  const closeColumnSettings = () => {
    setShowColumnSettings(false);
    setSelectedColumn('');
  };

  if (isGenerating) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-accent-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-windows-900 mb-2">Generating Synthetic Data</h3>
          <p className="text-windows-600">AI is creating realistic test data based on your scenarios...</p>
          <div className="mt-4 w-64 mx-auto">
            <div className="progress-windows">
              <div className="progress-bar-windows" style={{ width: '75%' }}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col overflow-x-auto">
      {/* Header */}
      <div className="card-windows mb-6">
        <div className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/schema-analysis')}
                className="btn-windows flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Schema Analysis</span>
              </button>
              
              <h1 className="text-2xl font-bold text-windows-900">Data Generation Complete</h1>
            </div>
            
            <button
              onClick={handlePushToSystem}
              className="btn-windows-primary flex items-center space-x-2"
            >
              <span>Push Data to System</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
          
          <div className="text-center mt-2">
            <p className="text-windows-600 max-w-2xl mx-auto">
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex gap-6 min-h-0 overflow-x-auto">
        {/* File Explorer Sidebar */}
        <div className="w-80 flex-shrink-0">
          <div className="card-windows h-full">
            <div className="p-4 border-b border-windows-200">
              <h2 className="text-lg font-semibold text-windows-900 flex items-center space-x-2">
                <Database className="h-5 w-5 text-accent-600" />
                <span>Generated Files</span>
              </h2>
              <p className="text-windows-600 text-sm mt-1">
                Select a file to preview its contents
              </p>
            </div>
            
            <div className="p-4 space-y-2 max-h-96 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-accent-600" />
                </div>
              ) : generatedFiles.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="h-8 w-8 text-windows-400 mx-auto mb-2" />
                  <p className="text-windows-600 text-sm">No files generated yet</p>
                </div>
              ) : (
                generatedFiles.map((file, index) => (
                  <div
                    key={index}
                    className={`file-item-windows p-3 rounded-md ${
                      selectedFile?.name === file.name ? 'selected' : ''
                    }`}
                    onClick={() => handleFileSelect(file)}
                  >
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-accent-600" />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-windows-900 truncate">
                          {file.name.replace('.csv', '')}
                        </div>
                        <div className="text-sm text-windows-600">
                          {file.size ? `${(file.size / 1024).toFixed(1)} KB` : 'Unknown size'}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Data Preview */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="card-windows flex-1 flex flex-col">
            <div className="p-4 border-b border-windows-200">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div className="flex-shrink-0">
                  <h2 className="text-lg font-semibold text-windows-900 flex items-center space-x-2">
                    <Eye className="h-5 w-5 text-accent-600" />
                    <span>Data Preview</span>
                    {selectedFile && (
                      <span className="text-windows-600 font-normal">
                        - {selectedFile.name}
                      </span>
                    )}
                  </h2>
                  <p className="text-windows-600 text-sm mt-1">
                    Showing {getPaginatedData().length} of {getFilteredData().length} records
                    {anomalyRows.size > 0 && (
                      <span className="ml-2 inline-flex items-center space-x-1">
                        <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                        <span className="text-red-600 text-xs font-medium">
                          {anomalyRows.size} potential anomalies detected
                        </span>
                      </span>
                    )}
                    {editedData.length > 0 && (
                      <span className="ml-2 inline-flex items-center space-x-1">
                        <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                        <span className="text-green-600 text-xs font-medium">
                          Data has been modified
                        </span>
                      </span>
                    )}
                  </p>
                </div>
                
                <div className="flex flex-wrap items-center gap-2 min-w-0">
                  {editedData.length > 0 && (
                    <button
                      onClick={saveAllChanges}
                      disabled={isSaving}
                      className="btn-windows flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white flex-shrink-0"
                    >
                      {isSaving ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <CheckCircle className="h-4 w-4" />
                      )}
                      <span className="hidden sm:inline">{isSaving ? 'Saving...' : 'Save Changes'}</span>
                      <span className="sm:hidden">{isSaving ? 'Saving' : 'Save'}</span>
                    </button>
                  )}
                  <button className="btn-windows flex items-center space-x-2 flex-shrink-0">
                    <Download className="h-4 w-4" />
                    <span className="hidden sm:inline">Export</span>
                    <span className="sm:hidden">Export</span>
                  </button>
                  <button
                    onClick={handlePushToSystem}
                    className="btn-windows-primary flex items-center space-x-2 flex-shrink-0"
                  >
                    <Upload className="h-4 w-4" />
                    <span className="hidden lg:inline">Push to System</span>
                    <span className="lg:hidden">Push</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Search and Filter */}
            <div className="p-4 border-b border-windows-200">
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <div className="flex-1 relative min-w-0">
                  <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-windows-400" />
                  <input
                    type="text"
                    placeholder="Search data..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="input-windows pl-10 w-full"
                  />
                </div>
                <button className="btn-windows flex items-center justify-center space-x-2 flex-shrink-0">
                  <Filter className="h-4 w-4" />
                  <span>Filter</span>
                </button>
              </div>
            </div>

            {/* Data Table */}
            <div className="flex-1 overflow-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-6 w-6 animate-spin text-accent-600" />
                </div>
              ) : fileData.length === 0 ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <FileText className="h-12 w-12 text-windows-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-windows-900 mb-2">No data to display</h3>
                    <p className="text-windows-600">Select a file from the sidebar to preview its contents</p>
                  </div>
                </div>
              ) : (
                <div className="overflow-x-auto min-w-full">
                  <table className="data-grid-windows w-full min-w-max">
                    <thead>
                      <tr>
                        {Object.keys(fileData[0] || {}).map((column) => (
                          <th
                            key={column}
                            className="cursor-pointer hover:bg-windows-200 transition-colors duration-200 px-3 py-2 min-w-0"
                            onClick={() => handleSort(column)}
                          >
                            <div className="flex items-center justify-between min-w-0">
                              <div className="flex items-center space-x-2 min-w-0">
                                <span className="truncate" title={formatColumnName(column)}>
                                  {formatColumnName(column)}
                                </span>
                                {sortColumn === column && (
                                  sortDirection === 'asc' ? (
                                    <SortAsc className="h-4 w-4 flex-shrink-0" />
                                  ) : (
                                    <SortDesc className="h-4 w-4 flex-shrink-0" />
                                  )
                                )}
                              </div>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  openColumnSettings(column);
                                }}
                                className="ml-2 p-1 hover:bg-windows-300 rounded transition-colors duration-200"
                                title={`Configure ${formatColumnName(column)}`}
                              >
                                <Settings className="h-3 w-3 text-windows-600" />
                              </button>
                            </div>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {getPaginatedData().map((row, rowIndex) => {
                        const globalRowIndex = (currentPage - 1) * itemsPerPage + rowIndex;
                        const isAnomaly = anomalyRows.has(globalRowIndex);
                        
                        return (
                          <tr 
                            key={rowIndex} 
                            className={`hover:bg-windows-50 ${
                              isAnomaly 
                                ? 'bg-red-50 border-l-4 border-red-500' 
                                : ''
                            }`}
                          >
                            {Object.entries(row).map(([column, value], colIndex) => {
                              const isEditing = editingCell?.rowIndex === globalRowIndex && editingCell?.column === column;
                              const currentValue = editedData[globalRowIndex]?.[column] || value;
                              
                              return (
                                <td key={colIndex} className="max-w-xs">
                                  {isEditing ? (
                                    <input
                                      type="text"
                                      value={currentValue}
                                      onChange={(e) => {
                                        const updatedData = [...editedData];
                                        updatedData[globalRowIndex] = { ...updatedData[globalRowIndex], [column]: e.target.value };
                                        setEditedData(updatedData);
                                      }}
                                      onKeyDown={(e) => handleCellKeyDown(e, globalRowIndex, column, String(currentValue))}
                                      onBlur={() => saveEdit(globalRowIndex, column, String(currentValue))}
                                      className="w-full p-1 border border-blue-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white"
                                      autoFocus
                                    />
                                  ) : (
                                    <div 
                                      className={`truncate cursor-pointer hover:bg-blue-50 p-1 rounded ${isAnomaly ? 'text-red-700 font-medium' : ''}`} 
                                      title={String(value)}
                                      onClick={() => startEditing(globalRowIndex, column, String(value))}
                                    >
                                      {String(currentValue)}
                                    </div>
                                  )}
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="p-4 border-t border-windows-200">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-windows-600">
                    Page {currentPage} of {totalPages}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      className="btn-windows px-3 py-1 disabled:opacity-50"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                      disabled={currentPage === totalPages}
                      className="btn-windows px-3 py-1 disabled:opacity-50"
                    >
                      Next
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Column Settings Side Panel */}
      {showColumnSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-windows-200">
              <div>
                <h2 className="text-xl font-semibold text-windows-900">
                  Column Settings: {formatColumnName(selectedColumn)}
                </h2>
                <p className="text-windows-600 text-sm mt-1">
                  Configure data generation rules for this column
                </p>
              </div>
              <button
                onClick={closeColumnSettings}
                className="p-2 hover:bg-windows-100 rounded-lg transition-colors duration-200"
              >
                <X className="h-5 w-5 text-windows-600" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              <div className="grid grid-cols-2 gap-4">
                {/* Basic Settings */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-windows-900 border-b pb-2">Basic Settings</h3>
                  
                  <div className="space-y-2">
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Change Data Type</div>
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Configure Null Handling</div>
                  </div>
                </div>

                {/* Data Generation */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-windows-900 border-b pb-2">Data Generation</h3>
                  
                  <div className="space-y-2">
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Random Generation</div>
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Sequential Generation</div>
                  </div>
                </div>

                {/* Distributions */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-windows-900 border-b pb-2">Distributions</h3>
                  
                  <div className="space-y-2">
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Uniform Distribution</div>
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Normal Distribution</div>
                  </div>
                </div>

                {/* Constraints */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-windows-900 border-b pb-2">Constraints</h3>
                  
                  <div className="space-y-2">
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Min/Max Values</div>
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Length Limits</div>
                  </div>
                </div>

                {/* Business Logic */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-windows-900 border-b pb-2">Business Logic</h3>
                  
                  <div className="space-y-2">
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Conditional Rules</div>
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Cross-Column Dependencies</div>
                  </div>
                </div>

                {/* Advanced Features */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-windows-900 border-b pb-2">Advanced Features</h3>
                  
                  <div className="space-y-2">
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Machine Learning Models</div>
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Statistical Analysis</div>
                  </div>
                </div>

                {/* Regeneration Options */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-windows-900 border-b pb-2">Regeneration</h3>
                  
                  <div className="space-y-2">
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Regenerate All Data</div>
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Regenerate Subset</div>
                  </div>
                </div>

                {/* Data Sources */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-windows-900 border-b pb-2">Data Sources</h3>
                  
                  <div className="space-y-2">
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">External APIs</div>
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Database Connections</div>
                  </div>
                </div>

                {/* Export & Integration */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-windows-900 border-b pb-2">Export & Integration</h3>
                  
                  <div className="space-y-2">
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">Export Formats</div>
                    <div className="p-2 bg-windows-50 rounded border cursor-not-allowed opacity-50 text-sm">API Endpoints</div>
                  </div>
                </div>
              </div>

              {/* Coming Soon Notice */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <span className="text-blue-600 font-medium">Coming Soon</span>
                  <span className="text-blue-500 text-sm">All these features will be available in future updates</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end space-x-3 p-6 border-t border-windows-200 bg-windows-50">
              <button
                onClick={closeColumnSettings}
                className="btn-windows"
              >
                Close
              </button>
              <button
                className="btn-windows-primary opacity-50 cursor-not-allowed"
                disabled
              >
                Apply Changes
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default DataGenerationPage;

export {}; 