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
