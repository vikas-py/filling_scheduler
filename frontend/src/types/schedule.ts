import type { Activity, KPIs, Lot } from './lot'

// ============================================================================
// Schedule Request/Response Types
// ============================================================================

export interface ScheduleRequest {
  name?: string | null
  lots_data: Lot[]
  strategy?: string
  config?: Record<string, any> | null
  start_time?: string | null // ISO datetime
}

export interface ScheduleResponse {
  id: number
  name: string | null
  strategy: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
  started_at: string | null
  completed_at: string | null
  error_message: string | null
}

export interface ScheduleResultResponse {
  makespan: number
  utilization: number
  changeovers: number
  lots_scheduled: number
  window_violations: number
  kpis: KPIs
  activities: Activity[]
}

export interface ScheduleDetailResponse extends ScheduleResponse {
  result: ScheduleResultResponse | null
}

export interface ScheduleListResponse {
  schedules: ScheduleResponse[]
  total: number
  page: number
  page_size: number
}

// ============================================================================
// Schedule Progress Types (WebSocket)
// ============================================================================

export interface ScheduleProgress {
  schedule_id: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number // 0-100
  current_step: string
  message: string
  started_at?: string
  completed_at?: string
  error?: string
}

// ============================================================================
// Schedule Export Types
// ============================================================================

export type ExportFormat = 'json' | 'csv'

export interface ExportOptions {
  format: ExportFormat
  include_kpis?: boolean
  include_activities?: boolean
}

// ============================================================================
// Schedule Store Types
// ============================================================================

export interface ScheduleState {
  schedules: ScheduleResponse[]
  currentSchedule: ScheduleDetailResponse | null
  isLoading: boolean
  error: string | null
  total: number
  page: number
  pageSize: number
  fetchSchedules: (page?: number, pageSize?: number) => Promise<void>
  fetchSchedule: (id: number) => Promise<void>
  createSchedule: (request: ScheduleRequest) => Promise<ScheduleResponse>
  deleteSchedule: (id: number) => Promise<void>
  exportSchedule: (id: number, format: ExportFormat) => Promise<Blob>
}
