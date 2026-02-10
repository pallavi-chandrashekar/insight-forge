import axios, { AxiosError } from 'axios'
import type { User, Token, Dataset, DatasetPreview, Query, QueryHistoryItem, Visualization, VizSuggestion, NLVizResponse, SmartImportResponse, SmartImportContextResult, SupportedPlatforms, KaggleImportResponse, ContextChatRequest, ContextChatResponse, DatasetDeleteInfo, DatasetDeleteResult, KaggleCredentials, LLMSettings, LLMProvider } from '../types'

// Use environment variable for API URL, fallback to /api for local dev
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
        const { access_token, refresh_token } = response.data

        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: async (email: string, password: string, full_name?: string) => {
    const { data } = await api.post<User>('/auth/register', { email, password, full_name })
    return data
  },

  login: async (email: string, password: string) => {
    const { data } = await api.post<Token>('/auth/login', { email, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  getCurrentUser: async () => {
    const { data } = await api.get<User>('/auth/me')
    return data
  },

  getKaggleCredentials: async () => {
    const { data } = await api.get<KaggleCredentials>('/auth/kaggle-credentials')
    return data
  },

  saveKaggleCredentials: async (kaggle_username: string, kaggle_key: string) => {
    const { data } = await api.post<KaggleCredentials>('/auth/kaggle-credentials', {
      kaggle_username,
      kaggle_key,
    })
    return data
  },

  deleteKaggleCredentials: async () => {
    await api.delete('/auth/kaggle-credentials')
  },

  // LLM Settings
  getLLMSettings: async () => {
    const { data } = await api.get<LLMSettings>('/auth/llm-settings')
    return data
  },

  saveLLMSettings: async (provider: string, api_key: string) => {
    const { data } = await api.post<LLMSettings>('/auth/llm-settings', {
      provider,
      api_key,
    })
    return data
  },

  deleteLLMSettings: async () => {
    await api.delete('/auth/llm-settings')
  },

  getLLMProviders: async () => {
    const { data } = await api.get<{ providers: LLMProvider[] }>('/auth/llm-providers')
    return data.providers
  },
}

// Dataset API
export const datasetAPI = {
  upload: async (file: File, name: string, description?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    if (description) formData.append('description', description)

    const { data } = await api.post<Dataset>('/datasets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  importFromUrl: async (name: string, url: string, description?: string) => {
    const { data } = await api.post<Dataset>('/datasets/from-url', { name, url, description })
    return data
  },

  scrapeWebpage: async (name: string, url: string, selector?: string, description?: string) => {
    const { data } = await api.post<Dataset>('/datasets/scrape', {
      name,
      url,
      selector,
      description,
    })
    return data
  },

  list: async () => {
    const { data } = await api.get<Dataset[]>('/datasets/')
    return data
  },

  get: async (id: string) => {
    const { data } = await api.get<Dataset>(`/datasets/${id}`)
    return data
  },

  preview: async (id: string, limit = 100) => {
    const { data } = await api.get<DatasetPreview>(`/datasets/${id}/preview`, {
      params: { limit },
    })
    return data
  },

  getDeleteInfo: async (id: string) => {
    const { data } = await api.get<DatasetDeleteInfo>(`/datasets/${id}/delete-info`)
    return data
  },

  delete: async (
    id: string,
    options: { deleteContext?: boolean; deleteLinkedDatasets?: boolean } = {}
  ) => {
    const { deleteContext = true, deleteLinkedDatasets = false } = options
    const { data } = await api.delete<DatasetDeleteResult>(`/datasets/${id}`, {
      params: {
        delete_context: deleteContext,
        delete_linked_datasets: deleteLinkedDatasets,
      },
    })
    return data
  },
}

// Query API
export const queryAPI = {
  execute: async (dataset_id: string, query_type: string, query: string, name?: string) => {
    const { data } = await api.post<Query>('/query/execute', {
      dataset_id,
      query_type,
      query,
      name,
    })
    return data
  },

  naturalLanguage: async (dataset_id: string, question: string, name?: string) => {
    const { data } = await api.post<Query>('/query/natural-language', {
      dataset_id,
      question,
      name,
    })
    return data
  },

  history: async (dataset_id?: string) => {
    const { data } = await api.get<QueryHistoryItem[]>('/query/history', {
      params: dataset_id ? { dataset_id } : {},
    })
    return data
  },

  get: async (id: string) => {
    const { data } = await api.get<Query>(`/query/${id}`)
    return data
  },
}

// Visualization API
export const visualizationAPI = {
  generate: async (
    dataset_id: string,
    chart_type: string,
    config: any,
    name?: string,
    description?: string,
    query_id?: string
  ) => {
    const { data } = await api.post<Visualization>('/visualize/generate', {
      dataset_id,
      chart_type,
      config,
      name,
      description,
      query_id,
    })
    return data
  },

  suggest: async (dataset_id: string) => {
    const { data } = await api.post<VizSuggestion[]>('/visualize/suggest', null, {
      params: { dataset_id }
    })
    return data
  },

  list: async (dataset_id?: string) => {
    const { data } = await api.get<Visualization[]>('/visualize/', {
      params: dataset_id ? { dataset_id } : {},
    })
    return data
  },

  get: async (id: string) => {
    const { data } = await api.get<Visualization>(`/visualize/${id}`)
    return data
  },

  delete: async (id: string) => {
    await api.delete(`/visualize/${id}`)
  },

  fromNaturalLanguage: async (dataset_id: string, description: string, name?: string) => {
    const { data } = await api.post<NLVizResponse>('/visualize/from-natural-language', {
      dataset_id,
      description,
      name,
    })
    return data
  },
}

// Smart Import API
export const smartImportAPI = {
  analyzeUrl: async (url: string, dataset_name?: string) => {
    const { data} = await api.post<SmartImportResponse>('/smart-import/analyze-url', {
      url,
      dataset_name,
    })
    return data
  },

  createContextFromUrl: async (url: string, dataset_name?: string) => {
    const { data } = await api.post<SmartImportContextResult>('/smart-import/create-context-from-url', {
      url,
      dataset_name,
    })
    return data
  },

  getSupportedPlatforms: async () => {
    const { data } = await api.get<SupportedPlatforms>('/smart-import/supported-platforms')
    return data
  },

  importFromKaggle: async (
    url: string,
    dataset_name: string,
    options: {
      kaggle_username?: string
      kaggle_key?: string
      create_context?: boolean
      save_credentials?: boolean
    } = {}
  ) => {
    const { data } = await api.post<KaggleImportResponse>('/smart-import/import-from-kaggle', {
      url,
      dataset_name,
      kaggle_username: options.kaggle_username,
      kaggle_key: options.kaggle_key,
      create_context: options.create_context ?? true,
      save_credentials: options.save_credentials ?? false,
    })
    return data
  },

  validateKaggleCredentials: async (kaggle_username: string, kaggle_key: string) => {
    const { data } = await api.post('/smart-import/validate-kaggle-credentials', null, {
      params: { kaggle_username, kaggle_key }
    })
    return data
  },
}

// Context Chat API
export const contextChatAPI = {
  askQuestion: async (request: ContextChatRequest) => {
    const { data } = await api.post<ContextChatResponse>('/context-chat/ask', request)
    return data
  },

  getSummary: async (context_id: string) => {
    const { data } = await api.get(`/context-chat/${context_id}/summary`)
    return data
  },

  getTopics: async (context_id: string) => {
    const { data } = await api.get(`/context-chat/${context_id}/topics`)
    return data
  },
}

export default api
