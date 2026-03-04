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
  SortDesc
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useNotification } from '../context/NotificationContext';
import { apiService } from '../services/apiService';

const DataPreviewPage: React.FC = () => {
  const navigate = useNavigate();
  const { state, dispatch } = useApp();
  const { showSuccess, showError } = useNotification();
  const [loadedFiles, setLoadedFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [fileData, setFileData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(50);
  const [editingCell, setEditingCell] = useState<{rowIndex: number, column: string} | null>(null);
  const [editedData, setEditedData] = useState<any[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [showSchemaAnalysisLoading, setShowSchemaAnalysisLoading] = useState(false);
  const [schemaAnalysisStep, setSchemaAnalysisStep] = useState(0);

  useEffect(() => {
    if (!state.selectedProduct) {
      navigate('/create');
      return;
    }
    
    console.log('DataPreviewPage useEffect triggered:', {
      isDemoMode: state.isDemoMode,
      hasLoadedData: !!state.loadedData,
      loadedData: state.loadedData
    });
    
    // Check if we have real uploaded data
    if (state.loadedData && !state.isDemoMode) {
      console.log('Loading real data from context');
      loadRealData();
    }
    // Only load demo files if in demo mode
    else if (state.isDemoMode) {
      console.log('Loading demo data');
      loadDemoFiles();
    }
    else {
      console.log('No data available - showing empty state');
      setLoadedFiles([]);
      setFileData([]);
    }
  }, [state.selectedProduct, state.isDemoMode, state.loadedData, navigate]);

  const loadDemoFiles = async () => {
    setIsLoading(true);
    
    try {
      // Determine which folder to read from based on selected product
      const productType = state.selectedProduct?.id;
      console.log('Selected product:', state.selectedProduct);
      console.log('Product type:', productType);
      
      const folderPath = productType === 'functional-test-scenarios' ? 'input_data' : 'input_schemas';
      console.log('Selected folder path:', folderPath);
      
      // Try to fetch the list of CSV files from the appropriate folder
      let response;
      try {
        response = await fetch(`http://localhost:8000/${folderPath}`);
        console.log('API response status:', response.status);
      } catch (fetchError) {
        console.error('Fetch error:', fetchError);
        const errorMessage = fetchError instanceof Error ? fetchError.message : 'Unknown network error';
        throw new Error(`Network error: ${errorMessage}`);
      }
      
      if (!response.ok) {
        throw new Error(`Failed to fetch files from ${folderPath} - Status: ${response.status}`);
      }
      
      const files = await response.json();
      console.log('Files received:', files);
      
      if (!Array.isArray(files) || files.length === 0) {
        throw new Error(`No files found in ${folderPath}`);
      }
      
      // Create file objects with metadata
      const fileObjects = files.map((file: any) => ({
        name: file.name,
        size: file.size,
        path: `http://localhost:8000/${folderPath}/${file.name}`
      }));
      
      console.log('File objects created:', fileObjects);
      setLoadedFiles(fileObjects);
      
      if (fileObjects.length > 0) {
        setSelectedFile(fileObjects[0]);
        await loadFileData(fileObjects[0]);
      }
      
    } catch (error) {
      console.error('Failed to load demo files:', error);
      
      // Fallback: Create a mock file list based on known files
      const productType = state.selectedProduct?.id;
      const folderPath = productType === 'functional-test-scenarios' ? 'input_data' : 'input_schemas';
      
      const fallbackFiles = [
        { name: 'customer_info.csv', size: 145000, path: `http://localhost:8000/${folderPath}/customer_info.csv` },
        { name: 'credit_card_accounts.csv', size: 240000, path: `http://localhost:8000/${folderPath}/credit_card_accounts.csv` },
        { name: 'credit_card_products.csv', size: 1700, path: `http://localhost:8000/${folderPath}/credit_card_products.csv` },
        { name: 'credit_card_transactions.csv', size: 663000, path: `http://localhost:8000/${folderPath}/credit_card_transactions.csv` },
        { name: 'imobile_user_session.csv', size: 663000, path: `http://localhost:8000/${folderPath}/imobile_user_session.csv` }
      ];
      
      console.log('Using fallback files:', fallbackFiles);
      setLoadedFiles(fallbackFiles);
      
      if (fallbackFiles.length > 0) {
        setSelectedFile(fallbackFiles[0]);
        await loadFileData(fallbackFiles[0]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadRealData = () => {
    setIsLoading(true);
    
    try {
      console.log('Loading real data:', state.loadedData);
      console.log('Loaded data type:', typeof state.loadedData);
      console.log('Loaded data keys:', Object.keys(state.loadedData || {}));
      
      // Handle different types of loaded data
      let fileObjects: any[] = [];
      
      if (state.loadedData.files) {
        console.log('Processing file upload data:', state.loadedData.files);
        // File upload data
        fileObjects = Object.keys(state.loadedData.files).map(filename => {
          const fileData = state.loadedData.files[filename];
          console.log(`Processing file ${filename}:`, fileData);
          return {
            name: filename,
            size: fileData.data ? JSON.stringify(fileData.data).length * 2 : 0, // Approximate size
            path: `uploaded_${filename}`,
            data: fileData.data,
            columns: fileData.columns,
            rowCount: fileData.row_count
          };
        });
      } else if (state.loadedData.tables) {
        console.log('Processing database table data:', state.loadedData.tables);
        // Database data
        fileObjects = Object.keys(state.loadedData.tables).map(tableName => {
          const tableData = state.loadedData.tables[tableName];
          console.log(`Processing table ${tableName}:`, tableData);
          return {
            name: `${tableName}.csv`,
            size: tableData.data ? JSON.stringify(tableData.data).length * 2 : 0, // Approximate size
            path: `database_${tableName}`,
            data: tableData.data,
            columns: tableData.columns,
            rowCount: tableData.row_count
          };
        });
      } else {
        console.log('No files or tables found in loaded data');
      }
      
      console.log('Real data file objects created:', fileObjects);
      setLoadedFiles(fileObjects);
      
      if (fileObjects.length > 0) {
        setSelectedFile(fileObjects[0]);
        // For real data, we already have the data in memory, so we can set it directly
        if (fileObjects[0].data) {
          console.log('Setting file data directly:', fileObjects[0].data.length, 'rows');
          setFileData(fileObjects[0].data);
        } else {
          console.log('No data found in first file object');
        }
      } else {
        console.log('No file objects created from loaded data');
      }
      
    } catch (error) {
      console.error('Failed to load real data:', error);
      showError('Error', 'Failed to load uploaded data');
    } finally {
      setIsLoading(false);
    }
  };

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
    if (lines.length === 0) return [];
    
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
    
    return dataRows;
  };

  const loadFileData = async (file: any) => {
    setIsLoading(true);
    
    try {
      console.log('Loading file data for:', file.path);
      
      // Check if this is real data that's already in memory
      if (file.data && Array.isArray(file.data)) {
        console.log('Using real data from memory:', file.data.length, 'rows');
        setFileData(file.data);
        return;
      }
      
      // For demo files, fetch the CSV content from the server
      const response = await fetch(file.path);
      console.log('File response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch file: ${response.status} ${response.statusText}`);
      }
      
      const csvText = await response.text();
      console.log('CSV content length:', csvText.length);
      
      // Parse CSV content
      const parsedData = parseCSV(csvText);
      console.log('Parsed data:', parsedData.length, 'rows');
      
      setFileData(parsedData);
      
    } catch (error) {
      console.error('Failed to load file data:', error);
      showError('Error', `Failed to load file: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = (file: any) => {
    setSelectedFile(file);
    
    // If this is real data that's already in memory, set it directly
    if (file.data && Array.isArray(file.data)) {
      console.log('Setting real data directly:', file.data.length, 'rows');
      setFileData(file.data);
    } else {
      // For demo files, load the data
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
    console.log('startEditing called:', { rowIndex, column, value });
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

  const handleContinueToSchemaAnalysis = async () => {
    if (state.isDemoMode) {
      // Demo mode: Set the appropriate demo run based on product type
      const productType = state.selectedProduct?.id;
      let demoRunId;
      
      if (productType === 'synthetic-data-generation') {
        demoRunId = '2'; // Run 2 for synthetic data generation
      } else if (productType === 'functional-test-scenarios') {
        demoRunId = '3'; // Run 3 for functional test scenarios
      } else {
        demoRunId = '2'; // Default to run 2
      }
      
      // Set the demo run in the global state
      dispatch({ 
        type: 'SET_CURRENT_RUN', 
        payload: {
          run_id: demoRunId,
          has_schema: true,
          has_synthetic_data: true,
          has_validation: true,
          has_input_data: true,
          created_at: '2025-08-05T12:00:00.000Z'
        }
      });
      
      navigate('/schema-analysis');
    } else {
      // Real data sources: Trigger appropriate analysis based on product type
      try {
        const productType = state.selectedProduct?.id;
        
        // Get the run ID from the loaded data
        const runId = state.loadedData?.runId;
        if (!runId) {
          console.error('No run ID found in loaded data');
          showError('Error', 'No run ID found. Please go back and reload your data.');
          return;
        }
        
        // Determine the mode and endpoint based on product type
        let mode = 'full'; // Default mode
        let response;
        
        if (productType === 'synthetic-data-generation') {
          // For synthetic data generation, we need to generate data from schemas
          // This should call the synthetic data generation endpoint, not schema analysis
          console.log('Starting synthetic data generation for synthetic data generation product using existing run ID:', runId);
          response = await apiService.generateSyntheticData(runId, {
            default_records: 1000,
            priority_multipliers: {
              CRITICAL: 2.0,
              HIGH: 1.5,
              MEDIUM: 1.0,
              LOW: 0.5
            }
          });
        } else if (productType === 'functional-test-scenarios') {
          mode = 'full'; // Use full mode for functional test scenarios to generate comprehensive business logic
          console.log('Starting test scenario generation for functional test scenarios with mode:', mode, 'using existing run ID:', runId);
          response = await apiService.runTestScenarioGeneration(runId, mode);
        } else {
          // Default to schema analysis for unknown product types
          mode = 'full';
          console.log('Starting default schema analysis with mode:', mode, 'using existing run ID:', runId);
          response = await apiService.runSchemaAnalysis(runId, mode);
        }
        
        console.log('API Response received:', response);
        console.log('Response data:', response?.data);
        console.log('Response run_id:', response?.data?.run_id);
        
        // Handle different response structures based on product type
        let responseRunId;
        if (productType === 'synthetic-data-generation') {
          // generateSyntheticData returns { data: { data: { run_id: "..." } } }
          responseRunId = response?.data?.data?.run_id || response?.data?.run_id || response?.run_id;
        } else {
          // runTestScenarioGeneration returns { data: { run_id: "..." } }
          responseRunId = response?.data?.run_id;
        }
        
        if (responseRunId) {
          console.log('Analysis started successfully with run ID:', responseRunId);
          
          // Store the run information in context
          dispatch({ 
            type: 'SET_CURRENT_RUN', 
            payload: {
              run_id: responseRunId,
              has_schema: false, // Will be updated when analysis completes
              has_synthetic_data: false,
              has_validation: false,
              has_input_data: true, // We have input data from our sources
              created_at: new Date().toISOString()
            }
          });
          
          // Show loading state and poll for completion
          setShowSchemaAnalysisLoading(true);
          setSchemaAnalysisStep(0);
          
          // Show initial loading steps
          const steps = [
            'Initializing analysis',
            'Processing input data',
            'Analyzing data structure',
            'Generating business logic'
          ];
          
          // Show loading steps
          for (let i = 0; i < steps.length; i++) {
            setSchemaAnalysisStep(i);
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
          
          // Continue showing loading state and poll for completion
          setSchemaAnalysisStep(4); // Show "Waiting for completion" step
          
          // Poll for schema analysis completion
          let isComplete = false;
          let attempts = 0;
          const maxAttempts = 60; // 5 minutes max (5 seconds * 60)
          
          while (!isComplete && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds between checks
            attempts++;
            
            try {
              // Check if schema analysis is complete by checking run status
              const runStatus = await apiService.getRun(responseRunId);
              if (runStatus?.has_schema) {
                console.log('Schema analysis completed!');
                isComplete = true;
              } else {
                console.log(`Waiting for schema analysis... Attempt ${attempts}/${maxAttempts}`);
                // Update step to show progress
                setSchemaAnalysisStep(4 + (attempts % 3)); // Cycle through steps 4-6
              }
            } catch (error) {
              console.log('Error checking completion status:', error);
              // Continue polling
            }
          }
          
          if (isComplete) {
            setShowSchemaAnalysisLoading(false);
            // Navigate to schema analysis page
            navigate('/schema-analysis');
          } else {
            throw new Error('Schema analysis timed out after 5 minutes');
          }
        } else {
          console.error('Failed to start analysis: No run ID returned. Response:', response);
          showError('Error', 'Failed to start analysis. Please try again.');
        }
              } catch (error) {
          console.error('Failed to start analysis:', error);
          console.error('Error details:', {
            name: error instanceof Error ? error.name : 'Unknown',
            message: error instanceof Error ? error.message : 'Unknown error',
            stack: error instanceof Error ? error.stack : 'No stack trace'
          });
          showError('Error', `Failed to start analysis: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
  };

  const getSidebarTitle = () => {
    if (state.isDemoMode) {
      const productType = state.selectedProduct?.id;
      if (productType === 'functional-test-scenarios') {
        return 'Input Data Files';
      } else if (productType === 'synthetic-data-generation') {
        return 'Schema Files';
      }
      return 'Sample Data Files';
    } else {
      return 'Loaded Data Sources';
    }
  };

  const getPageDescription = () => {
    if (state.isDemoMode) {
      const productType = state.selectedProduct?.id;
      if (productType === 'functional-test-scenarios') {
        return 'Preview the input data files that will be used for functional test scenario generation.';
      } else if (productType === 'synthetic-data-generation') {
        return 'Preview the schema files that will be used for synthetic data generation.';
      }
      return 'Preview the loaded sample data files. You can explore the data structure and content before proceeding to schema analysis.';
    } else {
      return 'Preview the data loaded from your configured data sources. You can explore the data structure and content before proceeding to schema analysis.';
    }
  };

  return (
    <div className="h-full flex flex-col overflow-x-auto">
      {/* Header */}
      <div className="card-windows mb-6">
        <div className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/data-source')}
                className="btn-windows flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Data Source</span>
              </button>
              
              <div className="flex items-center space-x-3">
                <h1 className="text-2xl font-bold text-windows-900">Data Preview</h1>
                <span className="text-windows-600 text-lg">-</span>
                <p className="text-windows-600">
                  {getPageDescription()}
                </p>
              </div>
            </div>
            
            <button
              onClick={handleContinueToSchemaAnalysis}
              className="btn-windows-primary flex items-center space-x-2"
            >
              <span>Continue to Schema Analysis</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {!state.isDemoMode && !state.loadedData ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Database className="h-16 w-16 text-windows-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-windows-900 mb-2">No Data Available</h2>
            <p className="text-windows-600 mb-4">
              Please go back and either select "Use Sample Data" for demo mode or configure real data sources.
            </p>
            <button
              onClick={() => navigate('/data-source')}
              className="btn-windows-primary"
            >
              Back to Data Source
            </button>
          </div>
        </div>
      ) : (
         <div className="flex-1 flex gap-6 min-h-0 overflow-x-auto">
           {/* File Explorer Sidebar */}
           <div className="w-80 flex-shrink-0">
             <div className="card-windows h-full">
               <div className="p-4 border-b border-windows-200">
                 <h2 className="text-lg font-semibold text-windows-900 flex items-center space-x-2">
                   <Database className="h-5 w-5 text-accent-600" />
                   <span>{getSidebarTitle()}</span>
                 </h2>
                 <p className="text-windows-600 text-sm mt-1">
                   {state.isDemoMode 
                     ? 'Select a file to preview its contents'
                     : 'Select a data source to preview its contents'
                   }
                 </p>
               </div>
               
               <div className="p-4 space-y-2 max-h-96 overflow-y-auto">
                 {isLoading ? (
                   <div className="flex items-center justify-center py-8">
                     <Loader2 className="h-6 w-6 animate-spin text-accent-600" />
                   </div>
                 ) : loadedFiles.length === 0 ? (
                   <div className="text-center py-8">
                     <FileText className="h-8 w-8 text-windows-400 mx-auto mb-2" />
                     <p className="text-windows-600 text-sm">No files loaded</p>
                   </div>
                 ) : (
                   loadedFiles.map((file, index) => (
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
                             {state.isDemoMode 
                               ? file.name.replace('.csv', '')
                               : file.name
                             }
                           </div>
                           <div className="text-sm text-windows-600">
                             {file.size ? `${(file.size / 1024).toFixed(1)} KB` : 'Loading...'}
                             {file.rowCount && (
                               <span className="ml-2">• {file.rowCount.toLocaleString()} rows</span>
                             )}
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
                    onClick={handleContinueToSchemaAnalysis}
                    className="btn-windows-primary flex items-center space-x-2 flex-shrink-0"
                  >
                    <Upload className="h-4 w-4" />
                    <span className="hidden lg:inline">Continue to Schema Analysis</span>
                    <span className="lg:hidden">Continue</span>
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
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {getPaginatedData().map((row, rowIndex) => {
                        const globalRowIndex = (currentPage - 1) * itemsPerPage + rowIndex;
                        
                        return (
                          <tr 
                            key={rowIndex} 
                            className="hover:bg-windows-50"
                          >
                            {Object.entries(row).map(([column, value], colIndex) => {
                              const isEditing = editingCell?.rowIndex === globalRowIndex && editingCell?.column === column;
                              const currentValue = editedData[globalRowIndex]?.[column] || value;
                              
                              // Debug logging
                              if (isEditing) {
                                console.log('Cell is in editing mode:', { globalRowIndex, column, editingCell });
                              }
                              
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
                                      className="truncate cursor-pointer hover:bg-blue-50 p-1 rounded border border-transparent hover:border-blue-300 transition-all duration-200" 
                                      title={String(value)}
                                      onClick={() => {
                                        console.log('Cell clicked:', { globalRowIndex, column, value });
                                        startEditing(globalRowIndex, column, String(value));
                                      }}
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
      )}

      {/* Schema Analysis Loading Screen */}
      {showSchemaAnalysisLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="mb-6">
                <Loader2 className="h-12 w-12 animate-spin text-accent-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-windows-900 mb-2">Analyzing Data Schema</h3>
                <p className="text-windows-600">AI is analyzing your data structure and generating business logic...</p>
              </div>
              
              <div className="space-y-3">
                {[
                  'Initializing analysis',
                  'Processing input data',
                  'Analyzing data structure',
                  'Generating business logic',
                  'Waiting for analysis to complete',
                  'Verifying generated schema',
                  'Finalizing analysis results'
                ].map((step, index) => (
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
    </div>
  );
};

export default DataPreviewPage;

export {}; 