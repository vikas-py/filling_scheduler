// ============================================================================
// Lot Types
// ============================================================================

export interface Lot {
  lot_id: string
  product: string
  quantity: number
  priority?: number
  start_window?: string // ISO datetime
  end_window?: string // ISO datetime
  vial_type?: string
  due_date?: string // ISO datetime
  [key: string]: any // Allow additional properties
}

// ============================================================================
// Activity Types
// ============================================================================

export interface Activity {
  activity_id: string
  activity_type: 'filling' | 'cleaning' | 'changeover'
  line_id: string | number
  start_time: string // ISO datetime
  end_time: string // ISO datetime
  duration: number
  lot_id?: string
  product?: string
  vial_type?: string
  quantity?: number
  from_vial_type?: string // For changeovers
  to_vial_type?: string // For changeovers
}

// ============================================================================
// KPI Types
// ============================================================================

export interface KPIs {
  makespan: number
  utilization: number
  changeovers: number
  lots_scheduled: number
  window_violations: number
  total_filling_time?: number
  total_cleaning_time?: number
  total_changeover_time?: number
  avg_line_utilization?: number
  [key: string]: any // Allow additional KPIs
}
