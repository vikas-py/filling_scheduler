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
  kind?: string; // 'FILL', 'CLEAN', 'CHANGEOVER'
  lot_type?: string;
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
  makespan?: number;
  utilization?: number;
  changeovers?: number;
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

// Backend activity structure from schedule results
interface BackendActivity {
  start: string;
  end: string;
  kind: 'FILL' | 'CLEAN' | 'CHANGEOVER';
  lot_id: string | null;
  lot_type: string | null;
  note: string;
  duration_hours: number;
}

// Backend response structure for schedule detail
interface BackendScheduleDetail {
  id: number;
  name: string;
  strategy: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  result: {
    makespan: number;
    utilization: number;
    changeovers: number;
    lots_scheduled: number;
    window_violations: number;
    kpis_json: Record<string, unknown>;
    activities_json: BackendActivity[];
  } | null;
}

// Get a single schedule by ID
export const getSchedule = async (id: number): Promise<Schedule> => {
  // Backend uses /schedule/{id} (singular)
  const response = await api.get<BackendScheduleDetail>(`/schedule/${id}`);
  const backendData = response.data;

  // Transform backend activities to frontend format
  const activities: Activity[] = backendData.result?.activities_json.map((act, index) => {
    // Calculate hours from start of schedule
    const scheduleStart = new Date(backendData.started_at || backendData.created_at).getTime();
    const actStart = new Date(act.start).getTime();
    const actEnd = new Date(act.end).getTime();
    const startTimeHours = (actStart - scheduleStart) / (1000 * 60 * 60);
    const endTimeHours = (actEnd - scheduleStart) / (1000 * 60 * 60);

    return {
      id: `activity-${index}`,
      lot_id: act.lot_id || act.kind, // Use activity kind if no lot_id (for CLEAN, CHANGEOVER)
      filler_id: 0, // Backend doesn't track filler_id in single-filler schedules
      start_time: startTimeHours,
      end_time: endTimeHours,
      duration: act.duration_hours,
      num_units: undefined,
    };
  }) || [];

  // Transform backend response to frontend Schedule format
  const schedule: Schedule = {
    id: backendData.id,
    name: backendData.name,
    description: '', // Backend doesn't provide this
    status: backendData.status,
    strategy: backendData.strategy,
    config: {
      num_fillers: 1, // Backend doesn't provide this; default to 1 for single-filler schedules
    },
    created_at: backendData.created_at,
    updated_at: backendData.completed_at || backendData.started_at || backendData.created_at,
    num_lots: backendData.result?.lots_scheduled || 0,
    total_time: backendData.result?.makespan,
    activities,
  };

  return schedule;
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
