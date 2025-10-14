import axios from 'axios';
import type { StrategyType } from '../components/schedule/StrategySelector';
import { STORAGE_KEYS } from '../utils/constants';

// VITE_API_URL should include /api/v1 prefix (e.g., http://localhost:8000/api/v1)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface Activity {
  id: string;
  lot_id: string;
  filler_id: number;
  start_time: number;
  end_time: number;
  duration: number;
  num_units?: number;
}

export interface Schedule {
  id: number;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  strategy: string;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  num_lots: number;
  total_time?: number;
  result_file?: string;
  activities?: Activity[];
}

export interface ScheduleCreateRequest {
  name: string;
  description?: string;
  strategy: StrategyType;
  config: Record<string, unknown>;
  csv_file: File;
}

export interface ScheduleListResponse {
  schedules: Schedule[];
  total: number;
  page: number;
  page_size: number;
}

export interface ScheduleStats {
  total_schedules: number;
  active_schedules: number;
  completed_schedules: number;
  failed_schedules: number;
  strategies_distribution?: Record<string, number>;
  status_distribution?: Record<string, number>;
  page: number;
  page_size: number;
  total_filtered: number;
  schedules: Schedule[];
}

// Create a new schedule
export const createSchedule = async (data: ScheduleCreateRequest): Promise<Schedule> => {
  const formData = new FormData();
  formData.append('name', data.name);
  if (data.description) {
    formData.append('description', data.description);
  }
  formData.append('strategy', data.strategy);
  formData.append('config', JSON.stringify(data.config));
  formData.append('csv_file', data.csv_file);

  // Backend endpoint is /schedule (singular), not /schedules
  const response = await api.post<Schedule>('/schedule', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// Get list of schedules
export const getSchedules = async (
  page = 1,
  pageSize = 10,
  filters?: {
    status?: string;
    strategy?: string;
    search?: string;
  }
): Promise<ScheduleListResponse> => {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  if (filters?.status && filters.status !== 'all') {
    params.append('status', filters.status);
  }
  if (filters?.strategy && filters.strategy !== 'all') {
    params.append('strategy', filters.strategy);
  }
  if (filters?.search) {
    params.append('search', filters.search);
  }

  const response = await api.get<ScheduleListResponse>(`/schedules?${params.toString()}`);
  return response.data;
};

// Get a single schedule by ID
export const getSchedule = async (id: number): Promise<Schedule> => {
  // Backend uses /schedule/{id} (singular)
  const response = await api.get<Schedule>(`/schedule/${id}`);
  return response.data;
};

// Delete a schedule
export const deleteSchedule = async (id: number): Promise<void> => {
  // Backend uses /schedule/{id} (singular)
  await api.delete(`/schedule/${id}`);
};

// Get dashboard statistics
export const getScheduleStats = async (params?: {
  page?: number;
  page_size?: number;
  status?: string;
  strategy?: string;
  search?: string;
}): Promise<ScheduleStats> => {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.append('page', params.page.toString());
  if (params?.page_size) searchParams.append('page_size', params.page_size.toString());
  if (params?.status) searchParams.append('status', params.status);
  if (params?.strategy) searchParams.append('strategy', params.strategy);
  if (params?.search) searchParams.append('search', params.search);
  const response = await api.get<ScheduleStats>(`/schedules/stats?${searchParams.toString()}`);
  return response.data;
};

// Get available strategies
export const getStrategies = async (): Promise<string[]> => {
  const response = await api.get<{ strategies: string[] }>('/strategies');
  return response.data.strategies;
};

export default api;
