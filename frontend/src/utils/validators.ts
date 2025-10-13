import type { Lot } from '../types'

// ============================================================================
// CSV Validation
// ============================================================================

export const validateCSVFile = (file: File): { valid: boolean; error?: string } => {
  if (!file) {
    return { valid: false, error: 'No file provided' }
  }

  if (!file.name.endsWith('.csv')) {
    return { valid: false, error: 'File must be a CSV file' }
  }

  if (file.size === 0) {
    return { valid: false, error: 'File is empty' }
  }

  if (file.size > 10 * 1024 * 1024) {
    // 10MB limit
    return { valid: false, error: 'File size must be less than 10MB' }
  }

  return { valid: true }
}

// ============================================================================
// Lot Data Validation
// ============================================================================

export interface LotValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
}

export const validateLot = (lot: Lot): LotValidationResult => {
  const errors: string[] = []
  const warnings: string[] = []

  // Required fields
  if (!lot.lot_id || lot.lot_id.trim() === '') {
    errors.push('lot_id is required')
  }

  if (!lot.product || lot.product.trim() === '') {
    errors.push('product is required')
  }

  if (lot.quantity === undefined || lot.quantity === null) {
    errors.push('quantity is required')
  } else if (lot.quantity <= 0) {
    errors.push('quantity must be greater than 0')
  }

  // Optional but validated fields
  if (lot.priority !== undefined && (lot.priority < 1 || lot.priority > 10)) {
    warnings.push('priority should be between 1 and 10')
  }

  // Date validation
  if (lot.start_window) {
    try {
      const startDate = new Date(lot.start_window)
      if (isNaN(startDate.getTime())) {
        errors.push('start_window is not a valid date')
      }
    } catch {
      errors.push('start_window is not a valid date')
    }
  }

  if (lot.end_window) {
    try {
      const endDate = new Date(lot.end_window)
      if (isNaN(endDate.getTime())) {
        errors.push('end_window is not a valid date')
      }

      if (lot.start_window) {
        const startDate = new Date(lot.start_window)
        if (endDate <= startDate) {
          errors.push('end_window must be after start_window')
        }
      }
    } catch {
      errors.push('end_window is not a valid date')
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  }
}

export const validateLots = (lots: Lot[]): LotValidationResult => {
  const allErrors: string[] = []
  const allWarnings: string[] = []

  if (!lots || lots.length === 0) {
    return {
      valid: false,
      errors: ['At least one lot is required'],
      warnings: [],
    }
  }

  // Check for duplicate lot_ids
  const lotIds = lots.map(lot => lot.lot_id)
  const duplicates = lotIds.filter((id, index) => lotIds.indexOf(id) !== index)
  if (duplicates.length > 0) {
    allErrors.push(`Duplicate lot IDs found: ${[...new Set(duplicates)].join(', ')}`)
  }

  // Validate each lot
  lots.forEach((lot, index) => {
    const result = validateLot(lot)
    if (!result.valid) {
      allErrors.push(`Lot ${index + 1} (${lot.lot_id || 'unknown'}): ${result.errors.join(', ')}`)
    }
    if (result.warnings.length > 0) {
      allWarnings.push(
        `Lot ${index + 1} (${lot.lot_id || 'unknown'}): ${result.warnings.join(', ')}`
      )
    }
  })

  return {
    valid: allErrors.length === 0,
    errors: allErrors,
    warnings: allWarnings,
  }
}

// ============================================================================
// Email Validation
// ============================================================================

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// ============================================================================
// Password Validation
// ============================================================================

export interface PasswordValidationResult {
  valid: boolean
  errors: string[]
  strength: 'weak' | 'medium' | 'strong'
}

export const validatePassword = (password: string): PasswordValidationResult => {
  const errors: string[] = []
  let strength: 'weak' | 'medium' | 'strong' = 'weak'

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long')
  }

  const hasUpperCase = /[A-Z]/.test(password)
  const hasLowerCase = /[a-z]/.test(password)
  const hasNumbers = /\d/.test(password)
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password)

  if (!hasUpperCase) {
    errors.push('Password must contain at least one uppercase letter')
  }

  if (!hasLowerCase) {
    errors.push('Password must contain at least one lowercase letter')
  }

  if (!hasNumbers) {
    errors.push('Password must contain at least one number')
  }

  // Determine strength
  if (hasUpperCase && hasLowerCase && hasNumbers) {
    strength = 'medium'
  }
  if (hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar && password.length >= 12) {
    strength = 'strong'
  }

  return {
    valid: errors.length === 0,
    errors,
    strength,
  }
}

// ============================================================================
// Config Validation
// ============================================================================

export const validateConfig = (config: Record<string, any>): LotValidationResult => {
  const errors: string[] = []
  const warnings: string[] = []

  // Common config validations
  if (config.line_count !== undefined) {
    if (!Number.isInteger(config.line_count) || config.line_count < 1) {
      errors.push('line_count must be a positive integer')
    }
  }

  if (config.changeover_time !== undefined) {
    if (typeof config.changeover_time !== 'number' || config.changeover_time < 0) {
      errors.push('changeover_time must be a non-negative number')
    }
  }

  if (config.cleaning_time !== undefined) {
    if (typeof config.cleaning_time !== 'number' || config.cleaning_time < 0) {
      errors.push('cleaning_time must be a non-negative number')
    }
  }

  if (config.strategy_timeout !== undefined) {
    if (typeof config.strategy_timeout !== 'number' || config.strategy_timeout < 0) {
      errors.push('strategy_timeout must be a non-negative number')
    } else if (config.strategy_timeout > 3600) {
      warnings.push('strategy_timeout is very high (> 1 hour)')
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  }
}

// ============================================================================
// General Form Validation
// ============================================================================

export const validateRequired = (value: any): boolean => {
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim() !== ''
  if (Array.isArray(value)) return value.length > 0
  return true
}

export const validateMinLength = (value: string, minLength: number): boolean => {
  return value.length >= minLength
}

export const validateMaxLength = (value: string, maxLength: number): boolean => {
  return value.length <= maxLength
}

export const validateRange = (value: number, min: number, max: number): boolean => {
  return value >= min && value <= max
}
