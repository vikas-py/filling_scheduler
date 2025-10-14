import type { Schedule, Activity } from '@/api/schedules';

export const mockSchedule: Schedule = {
  id: 1,
  name: 'Test Schedule',
  strategy: 'LPT',
  status: 'completed',
  created_at: '2025-01-14T10:00:00Z',
  updated_at: '2025-01-14T10:05:00Z',
  num_lots: 50,
  total_time: 120.5,
  config: {
    num_fillers: 4,
    max_concurrent_lots: 10,
  },
  activities: [],
};

export const mockActivity: Activity = {
  id: '1',
  lot_id: 'LOT001',
  filler_id: 1,
  start_time: 0,
  end_time: 10,
  duration: 10,
  num_units: 100,
};

export const mockSchedules: Schedule[] = [
  mockSchedule,
  {
    ...mockSchedule,
    id: 2,
    name: 'Test Schedule 2',
    strategy: 'SPT',
    status: 'running',
  },
  {
    ...mockSchedule,
    id: 3,
    name: 'Test Schedule 3',
    strategy: 'CFS',
    status: 'failed',
  },
];

export const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
};

export const mockAuthResponse = {
  access_token: 'mock-jwt-token',
  token_type: 'bearer',
  user: mockUser,
};
