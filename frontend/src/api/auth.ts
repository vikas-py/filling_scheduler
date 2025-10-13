import { api } from './client'
import { API_ENDPOINTS } from '@/utils/constants'
import type { UserCreate, UserLogin, TokenResponse, UserResponse } from '@/types'

// ============================================================================
// Authentication API
// ============================================================================

export const authApi = {
  /**
   * Login with email and password
   * @param credentials - User login credentials
   * @returns JWT token response
   */
  login: async (credentials: UserLogin): Promise<TokenResponse> => {
    // FastAPI expects form data for OAuth2 password flow
    const formData = new URLSearchParams()
    formData.append('username', credentials.email) // OAuth2 uses 'username' field
    formData.append('password', credentials.password)

    const response = await api.post<TokenResponse>(API_ENDPOINTS.LOGIN, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    return response
  },

  /**
   * Register a new user
   * @param userData - User registration data
   * @returns Created user response
   */
  register: async (userData: UserCreate): Promise<UserResponse> => {
    return api.post<UserResponse>(API_ENDPOINTS.REGISTER, userData)
  },

  /**
   * Get current authenticated user
   * @returns Current user data
   */
  getCurrentUser: async (): Promise<UserResponse> => {
    return api.get<UserResponse>(API_ENDPOINTS.ME)
  },

  /**
   * Logout (client-side only - clears token)
   */
  logout: (): void => {
    // No server-side logout needed for JWT
    // Just clear local storage
  },
}
