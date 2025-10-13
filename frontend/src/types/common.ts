// ============================================================================
// Common/Shared Types
// ============================================================================

export interface ApiError {
  detail: string
  status_code?: number
  errors?: Array<{
    loc: string[]
    msg: string
    type: string
  }>
}

export interface PaginationParams {
  page?: number
  page_size?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// ============================================================================
// File Upload Types
// ============================================================================

export interface FileUploadResponse {
  filename: string
  size: number
  content_type: string
  rows: number | null
  columns: string[] | null
}

export interface FileValidationError {
  field: string
  message: string
  value: any
}

// ============================================================================
// WebSocket Types
// ============================================================================

export interface WebSocketMessage<T = any> {
  type: string
  data: T
  timestamp?: string
}

export interface WebSocketConnectionStatus {
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  reconnectAttempt: number
}

// ============================================================================
// UI State Types
// ============================================================================

export interface LoadingState {
  isLoading: boolean
  loadingMessage?: string
}

export interface ErrorState {
  hasError: boolean
  errorMessage: string | null
  errorDetails?: any
}

export type SortDirection = 'asc' | 'desc'

export interface SortConfig {
  field: string
  direction: SortDirection
}

export interface FilterConfig {
  field: string
  operator: 'eq' | 'ne' | 'gt' | 'lt' | 'gte' | 'lte' | 'contains' | 'in'
  value: any
}

// ============================================================================
// Route Types
// ============================================================================

export interface RouteConfig {
  path: string
  title: string
  icon?: string
  requireAuth?: boolean
  hideInNav?: boolean
}

// ============================================================================
// Theme Types
// ============================================================================

export type ThemeMode = 'light' | 'dark'

export interface ThemeConfig {
  mode: ThemeMode
  primaryColor?: string
  secondaryColor?: string
}

// ============================================================================
// Notification Types
// ============================================================================

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: string
  type: NotificationType
  message: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}
