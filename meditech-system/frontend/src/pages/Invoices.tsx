export default function Invoices() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Facturación</h1>
          <p className="text-gray-600 mt-1">Gestión de facturas y pagos</p>
        </div>
        <button className="btn-primary">
          Nueva Factura
        </button>
      </div>

      <div className="card">
        <div className="mb-4 flex gap-4">
          <input
            type="text"
            placeholder="Buscar por ID, QR, código de barras, nombre..."
            className="input-field flex-1 max-w-md"
          />
        </div>

        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">ID</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Paciente</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Fecha</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Total</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Estado</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={6} className="py-8 text-center text-gray-500">
                No hay facturas registradas. Comienza creando una nueva factura.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
