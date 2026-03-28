import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Activity,
  LayoutDashboard,
  Users,
  FileText,
  Microscope,
  Settings,
  LogOut,
  ChevronLeft,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Users, label: 'Pacientes', path: '/patients' },
  { icon: FileText, label: 'Facturación', path: '/invoices' },
  { icon: Microscope, label: 'Resultados', path: '/results' },
  { icon: Settings, label: 'Configuración', path: '/settings' },
]

export default function Sidebar() {
  const location = useLocation()
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  return (
    <motion.aside
      initial={{ x: -280 }}
      animate={{ x: 0 }}
      transition={{ type: 'spring', stiffness: 100 }}
      className="w-72 bg-white border-r border-gray-200 flex flex-col h-full shadow-lg"
    >
      {/* Header con logo */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-md">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-gray-900">MediTech</h1>
            <p className="text-xs text-gray-500">Sistema v3.0</p>
          </div>
        </div>
      </div>

      {/* Menú de navegación */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {menuItems.map((item, index) => {
          const isActive = location.pathname === item.path
          const Icon = item.icon

          return (
            <Link key={item.path} to={item.path}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 font-medium shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-primary-600' : ''}`} />
                <span>{item.label}</span>
                {isActive && (
                  <ChevronLeft className="w-4 h-4 ml-auto text-primary-600" />
                )}
              </motion.div>
            </Link>
          )
        })}
      </nav>

      {/* Usuario y logout */}
      <div className="p-4 border-t border-gray-100">
        <div className="bg-gray-50 rounded-lg p-4 mb-3">
          <p className="font-medium text-gray-900 text-sm truncate">{user?.full_name}</p>
          <p className="text-xs text-gray-500 truncate">{user?.email}</p>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
        >
          <LogOut className="w-4 h-4" />
          <span className="text-sm font-medium">Cerrar Sesión</span>
        </button>
      </div>
    </motion.aside>
  )
}
