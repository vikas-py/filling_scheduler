// ============================================================================
// Configuration Types
// ============================================================================

export interface ConfigTemplate {
  id: number
  user_id: number
  name: string
  description: string | null
  config_data: Record<string, any>
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface ConfigTemplateCreate {
  name: string
  description?: string | null
  config_data: Record<string, any>
  is_default?: boolean
}

export interface ConfigTemplateUpdate {
  name?: string
  description?: string | null
  config_data?: Record<string, any>
  is_default?: boolean
}

export interface ConfigTemplateListResponse {
  templates: ConfigTemplate[]
  total: number
}

export interface ConfigValidationResponse {
  is_valid: boolean
  errors: ValidationError[]
  warnings: string[]
}

export interface ValidationError {
  field: string
  message: string
  value: any
}

// ============================================================================
// Configuration Presets
// ============================================================================

export interface ConfigPreset {
  id: string
  name: string
  description: string
  icon: string
  config: Record<string, any>
}

export const CONFIG_PRESETS: ConfigPreset[] = [
  {
    id: 'fast',
    name: 'Fast',
    description: 'Quick scheduling with minimal optimization',
    icon: 'Speed',
    config: {
      line_count: 2,
      changeover_time: 15,
      cleaning_time: 30,
      strategy_timeout: 60,
    },
  },
  {
    id: 'balanced',
    name: 'Balanced',
    description: 'Good balance between speed and quality',
    icon: 'Balance',
    config: {
      line_count: 3,
      changeover_time: 30,
      cleaning_time: 45,
      strategy_timeout: 300,
    },
  },
  {
    id: 'optimal',
    name: 'Optimal',
    description: 'Best quality scheduling, may take longer',
    icon: 'Star',
    config: {
      line_count: 4,
      changeover_time: 30,
      cleaning_time: 60,
      strategy_timeout: 600,
    },
  },
]

// ============================================================================
// Config Store Types
// ============================================================================

export interface ConfigState {
  templates: ConfigTemplate[]
  currentTemplate: ConfigTemplate | null
  defaultTemplate: ConfigTemplate | null
  isLoading: boolean
  error: string | null
  fetchTemplates: () => Promise<void>
  fetchTemplate: (id: number) => Promise<void>
  createTemplate: (data: ConfigTemplateCreate) => Promise<ConfigTemplate>
  updateTemplate: (id: number, data: ConfigTemplateUpdate) => Promise<ConfigTemplate>
  deleteTemplate: (id: number) => Promise<void>
  setDefaultTemplate: (id: number) => Promise<void>
  getDefaultTemplate: () => Promise<ConfigTemplate>
  validateConfig: (config: Record<string, any>) => Promise<ConfigValidationResponse>
}
