// ============================================================================
// Authentication Types
// ============================================================================

export interface UserBase {
  email: string
}

export interface UserCreate extends UserBase {
  password: string
}

export interface UserLogin {
  email: string
  password: string
}

export interface UserResponse extends UserBase {
  id: number
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface TokenData {
  email: string | null
  user_id: number | null
}

// ============================================================================
// Authentication Store Types
// ============================================================================

export interface AuthState {
  user: UserResponse | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}
