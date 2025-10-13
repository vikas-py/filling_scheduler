import { format, parseISO, formatDistanceToNow, isValid } from 'date-fns'

// ============================================================================
// Date/Time Formatters
// ============================================================================

export const formatDateTime = (dateString: string | Date, formatString = 'PPpp'): string => {
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : dateString
    return isValid(date) ? format(date, formatString) : 'Invalid date'
  } catch {
    return 'Invalid date'
  }
}

export const formatDate = (dateString: string | Date): string => {
  return formatDateTime(dateString, 'PP')
}

export const formatTime = (dateString: string | Date): string => {
  return formatDateTime(dateString, 'p')
}

export const formatRelativeTime = (dateString: string | Date): string => {
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : dateString
    return isValid(date) ? formatDistanceToNow(date, { addSuffix: true }) : 'Invalid date'
  } catch {
    return 'Invalid date'
  }
}

// ============================================================================
// Number Formatters
// ============================================================================

export const formatNumber = (value: number, decimals = 2): string => {
  return value.toFixed(decimals)
}

export const formatPercent = (value: number, decimals = 1): string => {
  return `${(value * 100).toFixed(decimals)}%`
}

export const formatDuration = (seconds: number): string => {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.round(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }
}

export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`
}

// ============================================================================
// String Formatters
// ============================================================================

export const capitalize = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

export const titleCase = (str: string): string => {
  return str
    .split(/[\s_-]+/)
    .map(word => capitalize(word))
    .join(' ')
}

export const kebabToTitle = (str: string): string => {
  return titleCase(str.replace(/-/g, ' '))
}

export const truncate = (str: string, maxLength: number): string => {
  return str.length > maxLength ? `${str.slice(0, maxLength)}...` : str
}

// ============================================================================
// Strategy Name Formatter
// ============================================================================

export const formatStrategyName = (strategy: string): string => {
  const strategyNames: Record<string, string> = {
    'smart-pack': 'Smart Pack',
    'lpt-pack': 'LPT Pack',
    'spt-pack': 'SPT Pack',
    'hybrid-pack': 'Hybrid Pack',
    'cfs-pack': 'CFS Pack',
    'milp-opt': 'MILP Optimize',
  }
  return strategyNames[strategy] || titleCase(strategy)
}

// ============================================================================
// Status Formatter
// ============================================================================

export const formatStatus = (status: string): string => {
  const statusLabels: Record<string, string> = {
    pending: 'Pending',
    running: 'Running',
    completed: 'Completed',
    failed: 'Failed',
  }
  return statusLabels[status] || capitalize(status)
}

// ============================================================================
// Activity Type Formatter
// ============================================================================

export const formatActivityType = (type: string): string => {
  const typeLabels: Record<string, string> = {
    filling: 'Filling',
    cleaning: 'Cleaning',
    changeover: 'Changeover',
  }
  return typeLabels[type] || capitalize(type)
}

// ============================================================================
// KPI Formatters
// ============================================================================

export const formatKPI = (key: string, value: number): string => {
  const kpiFormatters: Record<string, (val: number) => string> = {
    makespan: val => formatDuration(val),
    utilization: val => formatPercent(val),
    changeovers: val => val.toString(),
    lots_scheduled: val => val.toString(),
    window_violations: val => val.toString(),
    execution_time: val => formatDuration(val),
  }

  const formatter = kpiFormatters[key] || ((val: number) => formatNumber(val))
  return formatter(value)
}

export const formatKPILabel = (key: string): string => {
  const kpiLabels: Record<string, string> = {
    makespan: 'Makespan',
    utilization: 'Utilization',
    changeovers: 'Changeovers',
    lots_scheduled: 'Lots Scheduled',
    window_violations: 'Window Violations',
    execution_time: 'Execution Time',
    total_filling_time: 'Total Filling Time',
    total_cleaning_time: 'Total Cleaning Time',
    total_changeover_time: 'Total Changeover Time',
    avg_line_utilization: 'Avg Line Utilization',
  }
  return kpiLabels[key] || titleCase(key)
}
