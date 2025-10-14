import { describe, it, expect, beforeEach } from 'vitest';
import { mockSchedule, mockSchedules, mockActivity } from '@/test/mocks';

describe('Schedule API Types', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('Mock Data', () => {
    it('has valid schedule structure', () => {
      expect(mockSchedule).toHaveProperty('id');
      expect(mockSchedule).toHaveProperty('name');
      expect(mockSchedule).toHaveProperty('status');
      expect(mockSchedule).toHaveProperty('strategy');
      expect(mockSchedule).toHaveProperty('config');
      expect(mockSchedule).toHaveProperty('created_at');
      expect(mockSchedule).toHaveProperty('updated_at');
      expect(mockSchedule).toHaveProperty('num_lots');
    });

    it('has valid activity structure', () => {
      expect(mockActivity).toHaveProperty('id');
      expect(mockActivity).toHaveProperty('lot_id');
      expect(mockActivity).toHaveProperty('filler_id');
      expect(mockActivity).toHaveProperty('start_time');
      expect(mockActivity).toHaveProperty('end_time');
      expect(mockActivity).toHaveProperty('duration');
    });

    it('has array of schedules', () => {
      expect(Array.isArray(mockSchedules)).toBe(true);
      expect(mockSchedules).toHaveLength(3);
    });

    it('schedule status values are valid', () => {
      const validStatuses = ['pending', 'running', 'completed', 'failed'];
      mockSchedules.forEach((schedule) => {
        expect(validStatuses).toContain(schedule.status);
      });
    });
  });

  describe('LocalStorage', () => {
    it('can store and retrieve token', () => {
      const token = 'test-jwt-token';
      localStorage.setItem('token', token);
      expect(localStorage.getItem('token')).toBe(token);
    });

    it('clears token on logout', () => {
      localStorage.setItem('token', 'test-token');
      localStorage.removeItem('token');
      expect(localStorage.getItem('token')).toBeNull();
    });
  });
});
