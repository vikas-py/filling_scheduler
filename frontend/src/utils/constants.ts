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
  // Auth (Note: /api/v1 is in API_BASE_URL, so these are relative paths)
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  ME: '/auth/me',

  // Schedules
  SCHEDULES: '/schedules', // List schedules (GET)
  SCHEDULE_CREATE: '/schedule', // Create schedule (POST) - singular
  SCHEDULE_BY_ID: (id: number) => `/schedule/${id}`, // Get/Delete schedule - singular
  SCHEDULE_EXPORT: (id: number, format: string) => `/schedule/${id}/export/${format}`,
  SCHEDULE_VALIDATE: '/schedule/validate',
  STRATEGIES: '/strategies', // Get strategies list

  // Comparisons
  COMPARISONS: '/comparisons',
  COMPARISON_BY_ID: (id: number) => `/comparisons/${id}`,
  COMPARE: '/compare',

  // Config Templates
  CONFIGS: '/config',
  CONFIG_BY_ID: (id: number) => `/config/${id}`,
  CONFIG_DEFAULT: '/config/default',
  CONFIG_SET_DEFAULT: (id: number) => `/config/${id}/set-default`,
  CONFIG_VALIDATE: '/config/validate',
  CONFIG_SYSTEM_DEFAULT: '/config/system-default',

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
