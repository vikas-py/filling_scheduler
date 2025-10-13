import { useAuthStore } from '@/store/authStore'

/**
 * Custom hook for accessing authentication state and actions
 */
export const useAuth = () => {
  const { user, token, isAuthenticated, login, register, logout, refreshUser } = useAuthStore()

  return {
    // State
    user,
    token,
    isAuthenticated,

    // Computed
    isAdmin: user?.is_superuser || false,
    userEmail: user?.email || null,

    // Actions
    login,
    register,
    logout,
    refreshUser,
  }
}
