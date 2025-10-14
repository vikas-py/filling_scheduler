import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { useWebSocket, type WebSocketMessage, type ScheduleUpdateMessage } from '@/hooks/useWebSocket';
import { success, error as errorToast, info } from '@/utils/toast';

interface RealTimeContextValue {
  status: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: Record<string, unknown>) => boolean;
  reconnect: () => void;
  isConnected: boolean;
  subscribeToSchedule: (scheduleId: string) => void;
  unsubscribeFromSchedule: (scheduleId: string) => void;
  scheduleUpdates: Map<string, ScheduleUpdateMessage['data']>;
}

const RealTimeContext = createContext<RealTimeContextValue | undefined>(undefined);

export const useRealTime = () => {
  const context = useContext(RealTimeContext);
  if (!context) {
    throw new Error('useRealTime must be used within RealTimeProvider');
  }
  return context;
};

interface RealTimeProviderProps {
  children: ReactNode;
}

export const RealTimeProvider = ({ children }: RealTimeProviderProps) => {
  const [scheduleUpdates, setScheduleUpdates] = useState<Map<string, ScheduleUpdateMessage['data']>>(
    new Map()
  );
  const [subscribedSchedules, setSubscribedSchedules] = useState<Set<string>>(new Set());

  const handleMessage = (message: WebSocketMessage) => {
    console.log('WebSocket message received:', message);

    // Handle schedule updates
    if (message.type === 'schedule_update') {
      const updateMessage = message as ScheduleUpdateMessage;
      const { id, status, message: updateText } = updateMessage.data;

      // Update local state
      setScheduleUpdates((prev) => {
        const next = new Map(prev);
        next.set(id, updateMessage.data);
        return next;
      });

      // Show toast notifications for important events
      if (status === 'completed') {
        success(`Schedule "${id}" completed successfully!`);
      } else if (status === 'failed') {
        errorToast(`Schedule "${id}" failed: ${updateText || 'Unknown error'}`);
      } else if (status === 'running') {
        info(`Schedule "${id}" is now running`);
      }
    }
  };

  const {
    status,
    lastMessage,
    sendMessage,
    reconnect,
    isConnected,
  } = useWebSocket({
    autoConnect: true,
    onMessage: handleMessage,
    onConnect: () => {
      console.log('WebSocket connected, resubscribing to schedules...');
      // Resubscribe to all schedules on reconnect
      subscribedSchedules.forEach((scheduleId) => {
        sendMessage({ type: 'subscribe', scheduleId });
      });
    },
  });

  const subscribeToSchedule = (scheduleId: string) => {
    if (!subscribedSchedules.has(scheduleId)) {
      setSubscribedSchedules((prev) => new Set(prev).add(scheduleId));
      if (isConnected) {
        sendMessage({ type: 'subscribe', scheduleId });
      }
    }
  };

  const unsubscribeFromSchedule = (scheduleId: string) => {
    if (subscribedSchedules.has(scheduleId)) {
      setSubscribedSchedules((prev) => {
        const next = new Set(prev);
        next.delete(scheduleId);
        return next;
      });
      if (isConnected) {
        sendMessage({ type: 'unsubscribe', scheduleId });
      }
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      subscribedSchedules.forEach((scheduleId) => {
        sendMessage({ type: 'unsubscribe', scheduleId });
      });
    };
  }, []);

  const value: RealTimeContextValue = {
    status,
    lastMessage,
    sendMessage,
    reconnect,
    isConnected,
    subscribeToSchedule,
    unsubscribeFromSchedule,
    scheduleUpdates,
  };

  return <RealTimeContext.Provider value={value}>{children}</RealTimeContext.Provider>;
};
