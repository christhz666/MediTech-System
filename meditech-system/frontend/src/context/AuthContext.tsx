import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

interface User {
  id: number
  username: string
  email: string
  full_name: string
  role_id: number
  branch_id: number
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  refreshTokenFunc: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,

      login: async (email: string, password: string) => {
        try {
          const response = await api.post('/auth/login', { email, password })
          const { access_token, refresh_token, user } = response.data
          
          set({
            user,
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          })
          
          // Configurar token para futuras peticiones
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        })
        delete api.defaults.headers.common['Authorization']
      },

      checkAuth: async () => {
        const { token, refreshTokenFunc } = get()
        
        if (!token) {
          set({ isLoading: false })
          return
        }

        try {
          // Configurar token actual
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
          
          // Verificar si el token es válido
          const response = await api.get('/auth/me')
          set({
            user: response.data,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          // Intentar refrescar token
          try {
            await refreshTokenFunc()
          } catch {
            // Si no se puede refrescar, cerrar sesión
            get().logout()
          }
        }
      },

      refreshTokenFunc: async () => {
        const { refreshToken } = get()
        
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken,
          })
          
          const { access_token, refresh_token } = response.data
          
          set({
            token: access_token,
            refreshToken: refresh_token,
          })
          
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        } catch (error) {
          throw error
        }
      },
    }),
    {
      name: 'meditech-auth',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// Hook para usar en componentes
export const useAuth = () => {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuth,
    refreshTokenFunc,
  } = useAuthStore()

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuth,
    refreshToken: refreshTokenFunc,
  }
}
