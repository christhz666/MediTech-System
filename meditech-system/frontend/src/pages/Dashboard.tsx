import { motion } from 'framer-motion'
import { Activity, Users, FileText, DollarSign, TrendingUp } from 'lucide-react'

const stats = [
  { icon: Users, label: 'Pacientes Totales', value: '1,234', change: '+12%', color: 'blue' },
  { icon: FileText, label: 'Facturas Hoy', value: '45', change: '+8%', color: 'green' },
  { icon: DollarSign, label: 'Ingresos del Mes', value: '$12,450', change: '+15%', color: 'purple' },
  { icon: TrendingUp, label: 'Estudios Realizados', value: '892', change: '+22%', color: 'orange' },
]

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Resumen general del sistema</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <p className="text-xs text-medical-green-600 mt-1">{stat.change}</p>
                </div>
                <div className={`w-12 h-12 rounded-xl bg-${stat.color}-100 flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Contenido principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Actividad Reciente</h2>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center space-x-3 py-2 border-b border-gray-100 last:border-0">
                <div className="w-2 h-2 rounded-full bg-primary-500" />
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Nuevo paciente registrado</p>
                  <p className="text-xs text-gray-500">Hace {i * 15} minutos</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Accesos Rápidos</h2>
          <div className="grid grid-cols-2 gap-4">
            <button className="btn-primary py-4">
              <Users className="w-5 h-5 mx-auto mb-2" />
              <span className="text-sm">Registrar Paciente</span>
            </button>
            <button className="btn-primary py-4">
              <FileText className="w-5 h-5 mx-auto mb-2" />
              <span className="text-sm">Nueva Factura</span>
            </button>
            <button className="btn-secondary py-4">
              <Microscope className="w-5 h-5 mx-auto mb-2" />
              <span className="text-sm">Ver Resultados</span>
            </button>
            <button className="btn-secondary py-4">
              <Activity className="w-5 h-5 mx-auto mb-2" />
              <span className="text-sm">Reportes</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Componente placeholder para Microscope
function Microscope({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
    </svg>
  )
}
