import type { Lot } from './lot'

// ============================================================================
// Comparison Request/Response Types
// ============================================================================

export interface CompareRequest {
  lots_data: Lot[]
  strategies: string[]
  config?: Record<string, any> | null
  start_time?: string | null // ISO datetime
}

export interface ComparisonResultItem {
  strategy: string
  makespan: number
  utilization: number
  changeovers: number
  lots_scheduled: number
  window_violations: number
  execution_time: number
}

export interface CompareResponse {
  results: ComparisonResultItem[]
  best_strategy: string
  sort_by: string
}

// ============================================================================
// Stored Comparison Types
// ============================================================================

export interface ComparisonRequest {
  name?: string | null
  lots_data: Lot[]
  strategies: string[]
  config?: Record<string, any> | null
  start_time?: string | null
}

export interface ComparisonResponse {
  id: number
  user_id: number
  name: string | null
  results: ComparisonResultItem[]
  best_strategy: string
  created_at: string
}

export interface ComparisonListResponse {
  comparisons: ComparisonResponse[]
  total: number
  page: number
  page_size: number
}

// ============================================================================
// Comparison Chart Data Types
// ============================================================================

export interface ComparisonChartData {
  strategy: string
  makespan: number
  utilization: number
  changeovers: number
  execution_time: number
}

export interface RadarChartData {
  strategy: string
  [key: string]: number | string // Allow dynamic metric keys
}

// ============================================================================
// Strategy Types
// ============================================================================

export interface Strategy {
  id: string
  name: string
  description: string
  performance: 'fast' | 'balanced' | 'optimal'
  best_for: string[]
  icon: string
}

export const AVAILABLE_STRATEGIES: Strategy[] = [
  {
    id: 'smart-pack',
    name: 'Smart Pack',
    description: 'Intelligent bin-packing with vial type grouping',
    performance: 'balanced',
    best_for: ['Mixed product types', 'Medium to large batches'],
    icon: 'Psychology',
  },
  {
    id: 'lpt-pack',
    name: 'LPT Pack',
    description: 'Longest Processing Time first',
    performance: 'fast',
    best_for: ['Large lots first', 'Quick scheduling'],
    icon: 'ArrowDownward',
  },
  {
    id: 'spt-pack',
    name: 'SPT Pack',
    description: 'Shortest Processing Time first',
    performance: 'fast',
    best_for: ['Small lots first', 'Fast turnaround'],
    icon: 'ArrowUpward',
  },
  {
    id: 'hybrid-pack',
    name: 'Hybrid Pack',
    description: 'Combines multiple strategies adaptively',
    performance: 'balanced',
    best_for: ['Complex scenarios', 'Balanced workload'],
    icon: 'Merge',
  },
  {
    id: 'cfs-pack',
    name: 'CFS Pack',
    description: 'Critical First Scheduling',
    performance: 'optimal',
    best_for: ['Priority-driven', 'Deadline-focused'],
    icon: 'PriorityHigh',
  },
  {
    id: 'milp-opt',
    name: 'MILP Optimize',
    description: 'Mixed Integer Linear Programming optimization',
    performance: 'optimal',
    best_for: ['Best quality', 'Optimal solutions'],
    icon: 'Functions',
  },
]

// ============================================================================
// Comparison Store Types
// ============================================================================

export interface ComparisonState {
  comparisons: ComparisonResponse[]
  currentComparison: ComparisonResponse | null
  isLoading: boolean
  error: string | null
  total: number
  page: number
  pageSize: number
  fetchComparisons: (page?: number, pageSize?: number) => Promise<void>
  fetchComparison: (id: number) => Promise<void>
  createComparison: (request: ComparisonRequest) => Promise<ComparisonResponse>
  deleteComparison: (id: number) => Promise<void>
  compareStrategies: (request: CompareRequest) => Promise<CompareResponse>
}
