import axios from 'axios';
import type { StrategyType } from '../components/schedule/StrategySelector';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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

  const response = await api.post<Schedule>('/schedules', formData, {
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
  const response = await api.get<Schedule>(`/schedules/${id}`);
  return response.data;
};

// Delete a schedule
export const deleteSchedule = async (id: number): Promise<void> => {
  await api.delete(`/schedules/${id}`);
};

// Get dashboard statistics
export const getScheduleStats = async (): Promise<ScheduleStats> => {
  const response = await api.get<ScheduleStats>('/schedules/stats');
  return response.data;
};

// Get available strategies
export const getStrategies = async (): Promise<string[]> => {
  const response = await api.get<{ strategies: string[] }>('/strategies');
  return response.data.strategies;
};

export default api;
