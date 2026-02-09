export interface User {
  id: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  tableau_server_url?: string
  created_at: string
  updated_at?: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Dataset {
  id: string
  name: string
  description?: string
  source_type: 'file' | 'url' | 'scrape'
  source_url?: string
  original_filename?: string
  file_size?: number
  file_type?: string
  schema?: DatasetSchema
  row_count?: number
  column_count?: number
  created_at: string
  updated_at?: string
}

export interface DatasetSchema {
  columns: ColumnInfo[]
  total_rows: number
  total_columns: number
}

export interface ColumnInfo {
  name: string
  dtype: string
  nullable: boolean
  sample_values: any[]
}

export interface DatasetPreview {
  dataset_id: string
  columns: string[]
  data: Record<string, any>[]
  total_rows: number
  preview_rows: number
}

export interface Query {
  id: string
  dataset_id: string
  name?: string
  query_type: 'sql' | 'natural_language' | 'pandas'
  original_input: string
  generated_query?: string
  result_preview?: Record<string, any>[]
  result_row_count?: string
  execution_time_ms?: string
  error_message?: string
  created_at: string
}

export interface QueryHistoryItem {
  id: string
  dataset_id: string
  dataset_name: string
  name?: string
  query_type: 'sql' | 'natural_language' | 'pandas'
  original_input: string
  created_at: string
}

export interface Visualization {
  id: string
  dataset_id: string
  query_id?: string
  name?: string
  description?: string
  chart_type: ChartType
  config: VizConfig
  chart_data?: any
  image_path?: string
  tableau_workbook_url?: string
  created_at: string
  updated_at?: string
}

export type ChartType =
  | 'bar'
  | 'line'
  | 'scatter'
  | 'pie'
  | 'histogram'
  | 'heatmap'
  | 'box'
  | 'area'
  | 'table'

export interface VizConfig {
  x_column?: string
  y_column?: string
  color_column?: string
  size_column?: string
  aggregation?: string
  title?: string
  x_label?: string
  y_label?: string
}

export interface VizSuggestion {
  chart_type: ChartType
  title: string
  description: string
  confidence: number
  config: VizConfig
  reasoning: string
}

export interface NLVizResponse {
  visualization: Visualization
  parsed_intent: {
    chart_type: ChartType
    title: string
    config: VizConfig
    reasoning: string
  }
  suggestions?: string[]
}

export interface SmartImportRequest {
  url: string
  dataset_name?: string
}

export interface SmartImportMessage {
  type: 'success' | 'info' | 'warning' | 'error'
  title: string
  message: string
  action: 'import_data' | 'create_context' | 'guide' | 'inspect'
  action_label: string
  details?: string
}

export interface SmartImportResponse {
  url_type: string
  platform?: string
  message: SmartImportMessage
  can_import_data: boolean
  can_create_context: boolean
  documentation_content?: string
}

export interface SmartImportContextResult {
  success: boolean
  context_id: string
  context_name: string
  message: string
}

export interface SupportedPlatforms {
  data_platforms: {
    supported_formats: string[]
    examples: string[]
  }
  documentation_platforms: {
    supported: string[]
    examples: string[]
  }
  dataset_platforms: {
    supported: string[]
    guidance: string
    examples: string[]
  }
}

export interface KaggleImportResponse {
  success: boolean
  dataset_id: string
  dataset_name: string
  row_count: number
  column_count: number
  context_id?: string
  context_name?: string
  context_error?: string
  credentials_saved?: boolean
}

export interface KaggleCredentials {
  has_credentials: boolean
  kaggle_username?: string
  is_valid?: boolean
}

export interface ContextChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ContextChatRequest {
  context_id: string
  question: string
  conversation_history?: ContextChatMessage[]
}

export interface ContextChatResponse {
  answer: string
  context_name: string
  context_id: string
  sources?: string[]
  follow_up_suggestions?: string[]
}

export interface DatasetDeleteInfo {
  dataset_id: string
  dataset_name: string
  has_context: boolean
  context_id?: string
  context_name?: string
  other_datasets: Array<{ id: string; name: string }>
  can_delete_directly: boolean
}

export interface DatasetDeleteResult {
  success: boolean
  message: string
  deleted_datasets: Array<{ id: string; name: string }>
  deleted_context?: { id: string; name: string }
}
