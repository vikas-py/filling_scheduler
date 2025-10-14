import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from '@/components/common/ProtectedRoute'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import { Dashboard } from '@/pages/Dashboard'
import { SchedulesList } from '@/pages/SchedulesList';
import { ScheduleCreate } from '@/pages/ScheduleCreate'
import { ScheduleDetail } from '@/pages/ScheduleDetail'
import { Compare } from '@/pages/Compare'
import { Config } from '@/pages/Config'
import { ROUTES } from '@/utils/constants'

export const router = createBrowserRouter([
  // Public routes
  {
    path: ROUTES.LOGIN,
    element: <Login />,
  },
  {
    path: ROUTES.REGISTER,
    element: <Register />,
  },

  // Protected routes with layout
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to={ROUTES.DASHBOARD} replace />,
      },
      {
        path: ROUTES.DASHBOARD,
        element: <Dashboard />,
      },
      // Placeholder routes (to be implemented in next phases)
      {
        path: ROUTES.SCHEDULES,
        element: <SchedulesList />,
      },
      {
        path: ROUTES.SCHEDULE_NEW,
        element: <ScheduleCreate />,
      },
      {
        path: '/schedules/:id',
        element: <ScheduleDetail />,
      },
      {
        path: ROUTES.COMPARE,
        element: <Compare />,
      },
      {
        path: ROUTES.CONFIG,
        element: <Config />,
      },
      {
        path: ROUTES.PROFILE,
        element: <div>Profile Page (Coming Soon)</div>,
      },
    ],
  },

  // 404 - Not Found
  {
    path: '*',
    element: <div>404 - Page Not Found</div>,
  },
])
