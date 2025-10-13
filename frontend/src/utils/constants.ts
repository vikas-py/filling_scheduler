// ============================================================================
// Application Constants
// ============================================================================

export const APP_NAME = 'Filling Scheduler'
export const APP_VERSION = '0.1.0'
export const APP_DESCRIPTION = 'Production Filling Line Scheduler'

// ============================================================================
// API Constants
// ============================================================================

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/api/v1/auth/login',
  REGISTER: '/api/v1/auth/register',
  ME: '/api/v1/auth/me',

  // Schedules
  SCHEDULES: '/api/v1/schedules',
  SCHEDULE_BY_ID: (id: number) => `/api/v1/schedules/${id}`,
  SCHEDULE_EXPORT: (id: number, format: string) => `/api/v1/schedules/${id}/export/${format}`,
  SCHEDULE_VALIDATE: '/api/v1/schedules/validate',
  STRATEGIES: '/api/v1/schedules/strategies',

  // Comparisons
  COMPARISONS: '/api/v1/comparisons',
  COMPARISON_BY_ID: (id: number) => `/api/v1/comparisons/${id}`,
  COMPARE: '/api/v1/compare',

  // Config Templates
  CONFIGS: '/api/v1/config',
  CONFIG_BY_ID: (id: number) => `/api/v1/config/${id}`,
  CONFIG_DEFAULT: '/api/v1/config/default',
  CONFIG_SET_DEFAULT: (id: number) => `/api/v1/config/${id}/set-default`,
  CONFIG_VALIDATE: '/api/v1/config/validate',
  CONFIG_SYSTEM_DEFAULT: '/api/v1/config/system-default',

  // Health
  ROOT: '/',
  HEALTH: '/health',
}

export const WS_ENDPOINTS = {
  SCHEDULE_PROGRESS: (scheduleId: number) => `/ws/schedules/${scheduleId}/progress`,
}

// ============================================================================
// Pagination Constants
// ============================================================================

export const DEFAULT_PAGE_SIZE = 20
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

// ============================================================================
// Schedule Status Constants
// ============================================================================

export const SCHEDULE_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const

export type ScheduleStatus = typeof SCHEDULE_STATUS[keyof typeof SCHEDULE_STATUS]

// ============================================================================
// Activity Type Constants
// ============================================================================

export const ACTIVITY_TYPES = {
  FILLING: 'filling',
  CLEANING: 'cleaning',
  CHANGEOVER: 'changeover',
} as const

export type ActivityType = typeof ACTIVITY_TYPES[keyof typeof ACTIVITY_TYPES]

// ============================================================================
// Strategy Constants
// ============================================================================

export const STRATEGIES = {
  SMART_PACK: 'smart-pack',
  LPT_PACK: 'lpt-pack',
  SPT_PACK: 'spt-pack',
  HYBRID_PACK: 'hybrid-pack',
  CFS_PACK: 'cfs-pack',
  MILP_OPT: 'milp-opt',
} as const

export type StrategyId = typeof STRATEGIES[keyof typeof STRATEGIES]

// ============================================================================
// Chart Colors
// ============================================================================

export const CHART_COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  info: '#2196f3',
  filling: '#4caf50',
  cleaning: '#ff9800',
  changeover: '#2196f3',
}

// ============================================================================
// File Upload Constants
// ============================================================================

export const ACCEPTED_FILE_TYPES = {
  CSV: '.csv',
  EXCEL: '.xlsx,.xls',
}

export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

// ============================================================================
// Time Constants
// ============================================================================

export const DEBOUNCE_DELAY = 300 // ms
export const POLLING_INTERVAL = 2000 // ms
export const WEBSOCKET_RECONNECT_DELAY = 3000 // ms
export const WEBSOCKET_MAX_RECONNECT_ATTEMPTS = 5

// ============================================================================
// Local Storage Keys
// ============================================================================

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER: 'user',
  THEME: 'theme',
  RECENT_STRATEGIES: 'recent_strategies',
  RECENT_CONFIGS: 'recent_configs',
} as const

// ============================================================================
// Route Paths
// ============================================================================

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  SCHEDULES: '/schedules',
  SCHEDULE_NEW: '/schedules/new',
  SCHEDULE_DETAIL: (id: number | string) => `/schedules/${id}`,
  COMPARE: '/compare',
  COMPARISONS: '/comparisons',
  COMPARISON_DETAIL: (id: number | string) => `/comparisons/${id}`,
  CONFIG: '/config',
  PROFILE: '/profile',
} as const
