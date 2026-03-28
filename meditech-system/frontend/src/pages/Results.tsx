export default function Results() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Resultados</h1>
          <p className="text-gray-600 mt-1">Búsqueda y visualización de resultados médicos</p>
        </div>
      </div>

      <div className="card">
        <div className="mb-4">
          <input
            type="text"
            placeholder="Buscar por ID de factura, QR, código de barras, nombre o cédula..."
            className="input-field max-w-2xl"
          />
          <p className="text-xs text-gray-500 mt-2">
            💡 También puedes escanear un código QR o código de barras directamente
          </p>
        </div>

        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">ID Factura</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Paciente</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Estudio</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Fecha</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Estado</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={6} className="py-8 text-center text-gray-500">
                No hay resultados disponibles. Realiza una búsqueda para encontrar resultados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
