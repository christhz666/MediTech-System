export default function Patients() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pacientes</h1>
          <p className="text-gray-600 mt-1">Gestión de pacientes y historial clínico</p>
        </div>
        <button className="btn-primary">
          Registrar Paciente
        </button>
      </div>

      <div className="card">
        <div className="mb-4">
          <input
            type="text"
            placeholder="Buscar por nombre, cédula o ID..."
            className="input-field max-w-md"
          />
        </div>

        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Nombre</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Cédula</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Teléfono</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Email</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={5} className="py-8 text-center text-gray-500">
                No hay pacientes registrados. Comienza registrando uno nuevo.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
