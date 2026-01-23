import { create } from 'zustand'
import { authAPI } from '../services/api'
import type { User } from '../types'

interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, full_name?: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  error: null,

  login: async (email: string, password: string) => {
    try {
      set({ isLoading: true, error: null })
      await authAPI.login(email, password)
      const user = await authAPI.getCurrentUser()
      set({ user, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false
      })
      throw error
    }
  },

  register: async (email: string, password: string, full_name?: string) => {
    try {
      set({ isLoading: true, error: null })
      await authAPI.register(email, password, full_name)
      await authAPI.login(email, password)
      const user = await authAPI.getCurrentUser()
      set({ user, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false
      })
      throw error
    }
  },

  logout: () => {
    authAPI.logout()
    set({ user: null })
  },

  fetchUser: async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        set({ isLoading: false })
        return
      }

      const user = await authAPI.getCurrentUser()
      set({ user, isLoading: false })
    } catch (error) {
      authAPI.logout()
      set({ user: null, isLoading: false })
    }
  },

  clearError: () => set({ error: null }),
}))

// Initialize auth state
useAuthStore.getState().fetchUser()
