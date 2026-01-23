import axios, { AxiosError } from 'axios'
import type { User, Token, Dataset, DatasetPreview, Query, QueryHistoryItem, Visualization, VizSuggestion } from '../types'

const api = axios.create({
  baseURL: '/api',
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

  delete: async (id: string) => {
    await api.delete(`/datasets/${id}`)
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
    const { data } = await api.post<VizSuggestion[]>('/visualize/suggest', { dataset_id })
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
}

export default api
