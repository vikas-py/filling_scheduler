import { create } from 'zustand'
import { authApi } from '@/api/auth'
import { STORAGE_KEYS } from '@/utils/constants'
import type { AuthState, UserResponse } from '@/types'

// ============================================================================
// Auth Store
// ============================================================================

export const useAuthStore = create<AuthState>((set, get) => ({
  // Initial state
  user: null,
  token: null,
  isAuthenticated: false,

  // Actions
  login: async (email: string, password: string) => {
    try {
      // Call login API
      const tokenResponse = await authApi.login({ email, password })

      // Store token
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, tokenResponse.access_token)
      set({ token: tokenResponse.access_token })

      // Fetch user data
      const user = await authApi.getCurrentUser()

      // Store user
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user))
      set({ user, isAuthenticated: true })
    } catch (error: any) {
      // Clear any partial state
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
      localStorage.removeItem(STORAGE_KEYS.USER)
      set({ user: null, token: null, isAuthenticated: false })
      throw error
    }
  },

  register: async (email: string, password: string) => {
    try {
      // Call register API
      await authApi.register({ email, password })

      // Auto-login after registration
      await get().login(email, password)
    } catch (error: any) {
      // Clear any partial state
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
      localStorage.removeItem(STORAGE_KEYS.USER)
      set({ user: null, token: null, isAuthenticated: false })
      throw error
    }
  },

  logout: () => {
    // Clear local storage
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USER)

    // Clear state
    set({ user: null, token: null, isAuthenticated: false })

    // Call API logout (no-op for JWT)
    authApi.logout()
  },

  refreshUser: async () => {
    try {
      const user = await authApi.getCurrentUser()
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user))
      set({ user, isAuthenticated: true })
    } catch (error) {
      // If refresh fails, logout
      get().logout()
      throw error
    }
  },
}))

// ============================================================================
// Initialize Auth State from LocalStorage
// ============================================================================

export const initializeAuth = () => {
  const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN)
  const userStr = localStorage.getItem(STORAGE_KEYS.USER)

  if (token && userStr) {
    try {
      const user: UserResponse = JSON.parse(userStr)
      useAuthStore.setState({
        token,
        user,
        isAuthenticated: true,
      })

      // Optionally refresh user data in background
      useAuthStore.getState().refreshUser().catch(() => {
        // If refresh fails, user will be logged out
      })
    } catch {
      // Invalid stored data, clear it
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
      localStorage.removeItem(STORAGE_KEYS.USER)
    }
  }
}
