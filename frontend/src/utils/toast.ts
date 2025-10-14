import toast from 'react-hot-toast';

// Toast utility functions for consistent notifications across the app

export const toastUtils = {
  // Success notifications
  success: (message: string, duration?: number) => {
    return toast.success(message, {
      duration: duration || 4000,
      position: 'top-right',
      style: {
        background: '#4caf50',
        color: '#fff',
      },
      iconTheme: {
        primary: '#fff',
        secondary: '#4caf50',
      },
    });
  },

  // Error notifications
  error: (message: string, duration?: number) => {
    return toast.error(message, {
      duration: duration || 6000,
      position: 'top-right',
      style: {
        background: '#f44336',
        color: '#fff',
      },
      iconTheme: {
        primary: '#fff',
        secondary: '#f44336',
      },
    });
  },

  // Info notifications
  info: (message: string, duration?: number) => {
    return toast(message, {
      duration: duration || 4000,
      position: 'top-right',
      icon: 'ℹ️',
      style: {
        background: '#2196f3',
        color: '#fff',
      },
    });
  },

  // Warning notifications
  warning: (message: string, duration?: number) => {
    return toast(message, {
      duration: duration || 5000,
      position: 'top-right',
      icon: '⚠️',
      style: {
        background: '#ff9800',
        color: '#fff',
      },
    });
  },

  // Loading notifications (returns toast id for updating)
  loading: (message: string) => {
    return toast.loading(message, {
      position: 'top-right',
    });
  },

  // Promise-based notifications (auto-updates)
  promise: <T,>(
    promise: Promise<T>,
    messages: {
      loading: string;
      success: string;
      error: string;
    }
  ) => {
    return toast.promise(
      promise,
      {
        loading: messages.loading,
        success: messages.success,
        error: messages.error,
      },
      {
        position: 'top-right',
        style: {
          minWidth: '250px',
        },
      }
    );
  },

  // Dismiss a specific toast
  dismiss: (toastId?: string) => {
    toast.dismiss(toastId);
  },

  // Dismiss all toasts
  dismissAll: () => {
    toast.dismiss();
  },
};

// Shorthand exports
export const { success, error, info, warning, loading, promise, dismiss, dismissAll } = toastUtils;
