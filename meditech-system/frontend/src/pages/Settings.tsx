export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Configuración</h1>
        <p className="text-gray-600 mt-1">Administración del sistema</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Sucursales</h2>
          <p className="text-gray-600 text-sm mb-4">Gestiona las sucursales del sistema</p>
          <button className="btn-primary w-full">
            Gestionar Sucursales
          </button>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Usuarios y Roles</h2>
          <p className="text-gray-600 text-sm mb-4">Administra usuarios y permisos</p>
          <button className="btn-primary w-full">
            Gestionar Usuarios
          </button>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Catálogo de Estudios</h2>
          <p className="text-gray-600 text-sm mb-4">Configura estudios y precios</p>
          <button className="btn-primary w-full">
            Gestionar Estudios
          </button>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Personalización</h2>
          <p className="text-gray-600 text-sm mb-4">Logos, colores y plantillas</p>
          <button className="btn-primary w-full">
            Personalizar Sistema
          </button>
        </div>
      </div>
    </div>
  )
}
