import { getApiBaseUrl, getWsUrl } from '../config/config';

const API_BASE_URL = getApiBaseUrl();

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || 'An error occurred',
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  private async handleResponse(response: Response): Promise<ApiResponse> {
    try {
      const data = await response.json();
      
      if (!response.ok) {
        return {
          error: data.detail || 'An error occurred',
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: 'Failed to parse response',
        status: response.status,
      };
    }
  }

  private handleError(error: any): ApiResponse {
    return {
      error: error instanceof Error ? error.message : 'Network error',
      status: 0,
    };
  }

  // Health check
  async healthCheck(): Promise<ApiResponse> {
    return this.request('/health');
  }

  // Get all runs
  async getRuns(): Promise<any[]> {
    const response = await this.request('/runs');
    return (response.data as any[]) || [];
  }

  // Get specific run
  async getRun(runId: string): Promise<any> {
    const response = await this.request(`/runs/${runId}`);
    return response.data;
  }

  // Run schema analysis
  async runSchemaAnalysis(runId?: string, mode: string = 'full'): Promise<any> {
    const response = await this.request('/schema-analysis', {
      method: 'POST',
      body: JSON.stringify({
        run_id: runId,
        mode,
      }),
    });
    return response.data;
  }

  // Run test scenario generation
  async runTestScenarioGeneration(runId?: string, mode: string = 'schema_only'): Promise<any> {
    const response = await this.request('/test-scenario-generation', {
      method: 'POST',
      body: JSON.stringify({
        run_id: runId,
        mode,
      }),
    });
    return response.data;
  }

  // Generate synthetic data
  async generateSyntheticData(runId: string, config: any = {}): Promise<any> {
    const response = await this.request('/generate-data', {
      method: 'POST',
      body: JSON.stringify({
        run_id: runId,
        config,
      }),
    });
    return response.data;
  }

  // Get test scenarios
  async getTestScenarios(runId: string): Promise<any> {
    console.log('API: Getting test scenarios for run:', runId);
    const response = await this.request(`/runs/${runId}/test-scenarios`);
    console.log('API: Test scenarios response:', response);
    return response.data;
  }

  // Generate test scenarios
  async generateTestScenarios(
    runId: string,
    selectedScenarios: number[],
    config: any = {}
  ): Promise<any> {
    const response = await this.request('/generate-test-scenarios', {
      method: 'POST',
      body: JSON.stringify({
        run_id: runId,
        selected_scenarios: selectedScenarios,
        config,
      }),
    });
    return response.data;
  }

  // Generate test scenario from prompt
  async generateScenarioFromPrompt(
    runId: string,
    tableName: string,
    userPrompt: string
  ): Promise<any> {
    const response = await this.request('/generate-scenario-from-prompt', {
      method: 'POST',
      body: JSON.stringify({
        run_id: runId,
        table_name: tableName,
        user_prompt: userPrompt,
      }),
    });
    return response.data;
  }

  // Run validation
  async runValidation(runId: string): Promise<any> {
    const response = await this.request('/validate', {
      method: 'POST',
      body: JSON.stringify({
        run_id: runId,
      }),
    });
    return response.data;
  }

  // Get run files
  async getRunFiles(runId: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/runs/${runId}/files`);
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Download file from run
  async downloadFile(
    runId: string,
    fileType: string,
    filename: string
  ): Promise<any> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/runs/${runId}/files/${fileType}/${filename}`
      );
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Get run configuration
  async getRunConfig(runId: string): Promise<any> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/runs/${runId}/config`
      );
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Run complete pipeline
  async runCompletePipeline(runId?: string, mode: string = 'full'): Promise<any> {
    const response = await this.request('/pipeline/complete', {
      method: 'POST',
      body: JSON.stringify({
        run_id: runId,
        mode,
      }),
    });
    return response.data;
  }

  // Test MySQL connection
  async testMysqlConnection(connection: any): Promise<ApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/test-mysql-connection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(connection),
      });
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Test Oracle connection
  async testOracleConnection(connection: any): Promise<ApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/test-oracle-connection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(connection),
      });
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Upload files
  async uploadFiles(files: File[], productType: string = 'functional-test-scenarios'): Promise<ApiResponse> {
    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      formData.append('product_type', productType);
      
      const response = await fetch(`${API_BASE_URL}/upload-files`, {
        method: 'POST',
        body: formData,
      });
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Load MySQL data
  async loadMysqlData(connection: any, productType: string = 'functional-test-scenarios'): Promise<ApiResponse> {
    try {
      const requestBody = { ...connection, product_type: productType };
      const response = await fetch(`${API_BASE_URL}/load-mysql-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Load Oracle data
  async loadOracleData(connection: any, productType: string = 'functional-test-scenarios'): Promise<ApiResponse> {
    try {
      const requestBody = { ...connection, product_type: productType };
      const response = await fetch(`${API_BASE_URL}/load-oracle-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Push data to database
  async pushDataToDatabase(
    runId: string, 
    databaseType: 'mysql' | 'oracle', 
    connection: any, 
    files: any[]
  ): Promise<ApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/push-data-to-database`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          run_id: runId,
          database_type: databaseType,
          connection: connection,
          files: files
        }),
      });
      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // WebSocket connection
  connectWebSocket(onMessage: (data: any) => void, onError?: (error: any) => void) {
    const ws = new WebSocket(`${getWsUrl()}/ws/logs`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  }
}

export const apiService = new ApiService(); 