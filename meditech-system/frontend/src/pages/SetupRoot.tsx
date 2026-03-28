import { useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, Shield, UserPlus } from 'lucide-react'
import { toast } from 'sonner'

export default function SetupRoot() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    branchName: '',
    branchCode: '',
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('Las contraseñas no coinciden')
      return
    }

    if (formData.password.length < 8) {
      toast.error('La contraseña debe tener al menos 8 caracteres')
      return
    }

    setIsLoading(true)

    try {
      // Intentar crear usuario ROOT
      const response = await fetch('/api/v1/auth/root/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          full_name: formData.fullName,
          branch_name: formData.branchName,
          branch_code: formData.branchCode,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Error en la configuración')
      }

      toast.success('¡Configuración completada! Redirigiendo al login...')
      
      setTimeout(() => {
        window.location.href = '/login'
      }, 2000)
    } catch (error: any) {
      toast.error(error.message || 'Error al configurar el sistema')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-medical-blue-50 p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-2xl"
      >
        <div className="glass-effect rounded-2xl shadow-xl p-8 backdrop-blur-sm bg-white/90">
          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
              className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl shadow-lg mb-4"
            >
              <Shield className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-medical-blue-600 bg-clip-text text-transparent">
              Configuración Inicial
            </h1>
            <p className="text-gray-600 mt-2 text-sm">
              Crea el usuario administrador principal (SUPER_ROOT)
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Datos del Usuario */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900 flex items-center">
                <UserPlus className="w-5 h-5 mr-2 text-primary-600" />
                Datos del Administrador
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre Completo *
                  </label>
                  <input
                    type="text"
                    value={formData.fullName}
                    onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                    className="input-field"
                    placeholder="Dr. Juan Pérez"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username *
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="input-field"
                    placeholder="admin"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="input-field"
                    placeholder="admin@meditech.com"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contraseña *
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="input-field"
                    placeholder="••••••••"
                    required
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmar Contraseña *
                  </label>
                  <input
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    className="input-field"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Datos de la Sucursal */}
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h3 className="font-semibold text-gray-900 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-primary-600" />
                Datos de la Primera Sucursal
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de Sucursal *
                  </label>
                  <input
                    type="text"
                    value={formData.branchName}
                    onChange={(e) => setFormData({ ...formData, branchName: e.target.value })}
                    className="input-field"
                    placeholder="Sede Principal"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Código de Sucursal *
                  </label>
                  <input
                    type="text"
                    value={formData.branchCode}
                    onChange={(e) => setFormData({ ...formData, branchCode: e.target.value })}
                    className="input-field"
                    placeholder="SEDE01"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Botón */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary py-3 text-base font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Configurando...' : 'Configurar Sistema'}
            </motion.button>
          </form>
        </div>
      </motion.div>
    </div>
  )
}
