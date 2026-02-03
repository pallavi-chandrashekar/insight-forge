/**
 * Context API Service
 * Handles all context-related API calls
 */
import api from './api';

export interface Context {
  id: string;
  name: string;
  version: string;
  description: string;
  context_type: 'single_dataset' | 'multi_dataset';
  status: 'draft' | 'active' | 'deprecated';
  tags?: string[];
  category?: string;
  owner?: string;
  created_by?: string;
  user_id: string;
  datasets_count: number;
  relationships_count: number;
  metrics_count: number;
  validation_status: string;
  created_at?: string;
  updated_at?: string;
}

export interface ContextDetail extends Context {
  parsed_yaml: any;
  markdown_content: string;
  datasets: any[];
  relationships?: any[];
  metrics?: any[];
  business_rules?: any[];
  filters?: any[];
  settings?: any;
  data_model?: any;
  glossary?: any[];
  validation_errors?: any[];
  validation_warnings?: any[];
}

export interface ContextStats {
  total_contexts: number;
  single_dataset_contexts: number;
  multi_dataset_contexts: number;
  active_contexts: number;
  failed_validation: number;
}

export interface GlossaryEntry {
  context_id: string;
  context_name: string;
  term: string;
  definition: string;
  synonyms?: string[];
  related_columns?: string[];
  examples?: string;
}

export interface Metric {
  context_id: string;
  context_name: string;
  id: string;
  name: string;
  description?: string;
  expression: string;
  data_type: string;
  format?: string;
  datasets?: string[];
  category?: string;
  owner?: string;
}

class ContextService {
  /**
   * Create a new context from content
   */
  async createContext(content: string, validate: boolean = true): Promise<Context> {
    const response = await api.post('/contexts/', null, {
      params: { content, validate }
    });
    return response.data;
  }

  /**
   * Upload a context file
   */
  async uploadContextFile(file: File, validate: boolean = true): Promise<Context> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(`/contexts/upload?validate=${validate}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * List all contexts with optional filters
   */
  async listContexts(params?: {
    context_type?: string;
    category?: string;
    status?: string;
    tags?: string[];
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<Context[]> {
    const response = await api.get('/contexts/', { params });
    return response.data;
  }

  /**
   * Get context statistics
   */
  async getStats(): Promise<ContextStats> {
    const response = await api.get('/contexts/stats');
    return response.data;
  }

  /**
   * Get context details by ID
   */
  async getContext(id: string): Promise<ContextDetail> {
    const response = await api.get(`/contexts/${id}`);
    return response.data;
  }

  /**
   * Download context as file
   */
  async downloadContext(id: string): Promise<Blob> {
    const response = await api.get(`/contexts/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Update context
   */
  async updateContext(id: string, content: string, validate: boolean = true): Promise<Context> {
    const response = await api.put(`/contexts/${id}`, null, {
      params: { content, validate }
    });
    return response.data;
  }

  /**
   * Delete context
   */
  async deleteContext(id: string): Promise<void> {
    await api.delete(`/contexts/${id}`);
  }

  /**
   * Search glossary terms
   */
  async searchGlossary(term: string): Promise<GlossaryEntry[]> {
    const response = await api.get('/contexts/glossary/search', {
      params: { term }
    });
    return response.data;
  }

  /**
   * Get metrics for a dataset
   */
  async getMetricsForDataset(datasetId: string): Promise<Metric[]> {
    const response = await api.get(`/contexts/datasets/${datasetId}/metrics`);
    return response.data;
  }
}

export default new ContextService();
