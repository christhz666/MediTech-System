# MediTech System - Sistema Integral de Gestión Médica

## 🏥 Sistema Completo para Clínicas y Hospitales

Sistema open source multi-sucursal con integración PACS (Orthanc), LIS (OpenELIS), facturación inteligente, y gestión completa de pacientes.

## ✨ Características Principales

### 🔐 Autenticación y Seguridad
- JWT con access token (30 min) + refresh token (7 días)
- Usuario ROOT para configuración inicial
- RBAC completo: Admin, Recepción, Doctor, Laboratorio, Radiólogo
- Permisos granulares por rol
- Hash de contraseñas con bcrypt
- Aislamiento total por sucursal

### 🏢 Multi-Sucursal
- IDs únicos de 4-5 dígitos por sucursal
- Puede haber ID 5021 en sucursal A y B simultáneamente
- Configuración independiente por sucursal
- Logos y personalización individual

### 👥 Gestión de Pacientes
- Registro completo con datos médicos
- Cédula opcional (acepta "MENOR" para niños)
- Búsqueda por nombre, cédula, ID, QR, código de barras
- Historial clínico completo cronológico
- Contacto de emergencia

### 💰 Facturación Inteligente
- Generación automática de IDs únicos (4-5 dígitos)
- Código de barras (Code128) y QR independientes
- Seguros médicos con cobertura porcentual
- Cálculo automático: total, seguro, paciente
- Estados: pending, partial, paid, cancelled
- Múltiples métodos de pago (efectivo, tarjeta, PayPal)

### 🔍 Búsqueda de Resultados
- Por ID de factura (4-5 dígitos)
- Por código de barras (scanner USB)
- Por código QR (móvil)
- Por nombre de paciente (muestra todo el historial)
- Por cédula
- Ordenado por fecha (más reciente primero)

### 🚫 Control de Pagos
- Bloqueo automático de resultados si hay deuda
- Mensaje amigable para pacientes
- Vista previa sin perder contexto actual
- Alerta visual para recepcionista

### 📊 Integraciones Médicas
- **Orthanc PACS**: Campo orthanc_study_uid para imágenes DICOM
- **OpenELIS LIS**: Campo openelis_order_id para laboratorio
- **HL7 v2.x**: Preparado para mensajes ORU^R01
- **FHIR R4**: Estructura compatible con recursos Patient, DiagnosticReport

### 🎨 Diseño UI/UX
- TailwindCSS con colores médicos personalizados
- Framer Motion para animaciones fluidas
- Lucide React icons
- Sonner toast notifications
- Responsive design completo
- Dark mode ready

## 🚀 Instalación Automática

### Requisito: Ubuntu/Debian Server

```bash
# Clonar repositorio
git clone https://github.com/christhz666/MediTech-System.git
cd MediTech-System

# Ejecutar instalación automática (30-40 minutos)
sudo bash scripts/install.sh
```

El script instalará automáticamente:
- PostgreSQL 14+
- Redis
- Nginx
- Orthanc (PACS)
- Python 3.10+
- Node.js 18+
- Todas las dependencias

### Post-Instalación

Al finalizar, el script mostrará:
- Credenciales del usuario ROOT
- URL de acceso al sistema
- URLs de servicios (Orthanc, API docs)

## 📁 Estructura del Proyecto

```
meditech-system/
├── backend/
│   ├── app/
│   │   ├── api/           # Endpoints REST
│   │   ├── core/          # Configuración y seguridad
│   │   ├── db/            # Base de datos y modelos
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── schemas/       # Schemas Pydantic
│   │   ├── services/      # Lógica de negocio
│   │   └── main.py        # Aplicación FastAPI
│   ├── scripts/
│   │   └── init_db.py     # Inicialización ROOT
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── pages/         # Páginas principales
│   │   ├── contexts/      # Contextos React
│   │   ├── services/      # Servicios API
│   │   └── App.tsx
│   ├── public/
│   └── package.json
├── config/
│   ├── nginx.conf
│   ├── orthanc.json
│   └── systemd/
├── scripts/
│   └── install.sh         # Script maestro de instalación
└── README.md
```

## 🔑 Endpoints API Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/root/setup` | Crear usuario ROOT |
| POST | `/api/v1/auth/login` | Login usuario |
| GET | `/api/v1/patients/` | Listar pacientes |
| POST | `/api/v1/patients/` | Registrar paciente |
| GET | `/api/v1/patients/{id}/history` | Historial completo |
| POST | `/api/v1/invoices/` | Crear factura con estudios |
| GET | `/api/v1/invoices/search/{term}` | Buscar por ID/QR/barras |
| POST | `/api/v1/invoices/{id}/pay` | Registrar pago |
| GET | `/api/v1/invoices/{id}/results` | Obtener resultados (si pagado) |
| POST | `/api/v1/admin/branches` | Crear sucursal |
| POST | `/api/v1/admin/roles` | Crear rol |
| POST | `/api/v1/admin/users` | Crear usuario |

**Documentación Swagger:** `http://localhost/api/docs`

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.10+**
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos principal
- **Redis** - Caché y colas
- **PyJWT** - Autenticación JWT
- **Bcrypt** - Hash de contraseñas
- **Pydantic** - Validación de datos

### Frontend
- **React 18+**
- **TypeScript**
- **TailwindCSS**
- **Framer Motion** - Animaciones
- **Lucide React** - Iconos
- **React Router** - Navegación
- **Axios** - Cliente HTTP

### Infraestructura
- **Nginx** - Reverse proxy
- **Orthanc** - Servidor PACS
- **OpenELIS** - Sistema LIS (integración)
- **Systemd** - Gestión de servicios

## 🔐 Roles del Sistema

1. **SUPER_ROOT**: Acceso total, configuración inicial
2. **ADMIN**: Gestión completa de sucursal
3. **RECEPCION**: Registro pacientes, facturación, cobros
4. **DOCTOR**: Ver resultados, agregar diagnósticos
5. **LABORATORIO**: Gestionar órdenes, cargar resultados
6. **RADIOLOGO**: Ver imágenes DICOM, informes

## 📋 Flujo de Trabajo Típico

1. **Registro Paciente**: Recepción registra paciente (cedula opcional)
2. **Selección Estudios**: Selecciona estudios a realizar
3. **Facturación**: Genera factura con ID único, QR y código de barras
4. **Pago**: Registra pago (parcial o total)
5. **Realización Estudios**: Laboratorio/Radiología realiza estudios
6. **Carga Resultados**: Sube resultados al sistema
7. **Entrega**: Paciente retira resultados (solo si pagó)

## 🔒 Seguridad

- Todos los endpoints protegidos con JWT
- Contraseñas hasheadas con bcrypt
- Aislamiento total entre sucursales
- Auditoría de todas las acciones
- HTTPS obligatorio en producción
- CORS configurado correctamente

## 📞 Soporte e Integraciones

### Equipos de Laboratorio
Soporta conexión directa vía HL7 v2.x para:
- Mindray
- Sysmex
- Roche
- Abbott
- Beckman Coulter

### Imágenes DICOM
- Almacenamiento en Orthanc
- Visualización con OHIF Viewer
- Vinculación por study UID

## 🎯 Próximas Mejoras (Roadmap)

- [ ] Middleware HL7 completo para analizadores
- [ ] Visor OHIF incrustado en frontend
- [ ] Facturación electrónica por país
- [ ] Módulo de citas médicas
- [ ] App móvil para pacientes
- [ ] Business Intelligence dashboards
- [ ] Integración con Stripe/PayPal

## 📄 Licencia

MIT License - Open Source

## 👨‍💻 Autor

Christhz 3.0 - Especialista en HealthTech

---

**¡Sistema listo para producción!** 🚀
