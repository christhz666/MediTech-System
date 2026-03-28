import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para agregar token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('meditech-auth')
    if (token) {
      try {
        const parsed = JSON.parse(token)
        if (parsed.state?.token) {
          config.headers.Authorization = `Bearer ${parsed.state.token}`
        }
      } catch (e) {
        // Ignorar errores de parseo
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const storedAuth = localStorage.getItem('meditech-auth')
        if (storedAuth) {
          const parsed = JSON.parse(storedAuth)
          const refreshToken = parsed.state?.refreshToken

          if (refreshToken) {
            const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
              refresh_token: refreshToken,
            })

            const { access_token, refresh_token } = response.data

            // Actualizar token en localStorage
            parsed.state.token = access_token
            parsed.state.refreshToken = refresh_token
            localStorage.setItem('meditech-auth', JSON.stringify(parsed))

            // Reintentar petición original
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return api(originalRequest)
          }
        }
      } catch (refreshError) {
        // Si no se puede refrescar, cerrar sesión
        localStorage.removeItem('meditech-auth')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api
