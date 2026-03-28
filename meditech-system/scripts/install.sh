#!/bin/bash
# MediTech System - Instalación Automática Completa
# Autor: Christhz 3.0
# Uso: sudo bash install.sh

set -e

echo "=============================================="
echo "  MediTech System v3.0 - Instalación Automática"
echo "  Autor: Christhz 3.0"
echo "=============================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${YELLOW}→ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    print_error "Por favor ejecutar como root (sudo bash install.sh)"
    exit 1
fi

# Directorio de instalación
INSTALL_DIR="/opt/meditech"
BACKUP_DIR="/opt/meditech-backup-$(date +%Y%m%d-%H%M%S)"

# ==================== ACTUALIZAR SISTEMA ====================
print_info "Actualizando sistema..."
apt-get update -y
apt-get upgrade -y

# ==================== INSTALAR DEPENDENCIAS DEL SISTEMA ====================
print_info "Instalando dependencias del sistema..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    curl \
    wget \
    git \
    unzip \
    libpq-dev \
    python3-dev \
    build-essential \
    supervisor

print_success "Dependencias instaladas"

# ==================== INSTALAR ORTHANC (PACS) ====================
print_info "Instalando Orthanc PACS..."
apt-get install -y orthanc orthanc-plugins

# Crear configuración personalizada de Orthanc
cat > /etc/orthanc/orthanc.json << 'EOF'
{
    "Name": "MediTech-PACS",
    "StorageDirectory": "/var/lib/orthanc/db",
    "IndexDirectory": "/var/lib/orthanc/db",
    "HttpPort": 8042,
    "DicomPort": 4242,
    "DicomAet": "MEDITECH",
    "RemoteAccessAllowed": true,
    "AuthenticationEnabled": true,
    "RegisteredUsers": [
        ["orthanc", "orthanc"]
    ],
    "OverwriteInstances": false,
    "StoreMD5ForAttachments": true,
    "LimitPatientRecords": 0,
    "LimitStudies": 0,
    "LimitModalities": 0
}
EOF

systemctl enable orthanc
systemctl start orthanc
print_success "Orthanc instalado y configurado"

# ==================== CONFIGURAR POSTGRESQL ====================
print_info "Configurando PostgreSQL..."

# Generar contraseña segura
DB_PASSWORD="meditech_$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 16)"

# Iniciar PostgreSQL
systemctl enable postgresql
systemctl start postgresql

# Crear usuario y base de datos
sudo -u postgres psql << EOF
CREATE USER meditech WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE meditech_db OWNER meditech;
GRANT ALL PRIVILEGES ON DATABASE meditech_db TO meditech;
\\c meditech_db
CREATE EXTENSION IF NOT EXISTS pgcrypto;
EOF

print_success "PostgreSQL configurado"

# ==================== CONFIGURAR REDIS ====================
print_info "Configurando Redis..."
systemctl enable redis-server
systemctl start redis-server
print_success "Redis configurado"

# ==================== COPIAR ARCHIVOS DEL PROYECTO ====================
print_info "Copiando archivos del proyecto..."

# Crear directorio de instalación
mkdir -p $INSTALL_DIR

# Copiar todo el proyecto
cp -r /workspace/meditech-system/* $INSTALL_DIR/

# Crear archivo .env con configuración
cat > $INSTALL_DIR/backend/app/.env << EOF
DATABASE_URL=postgresql://meditech:${DB_PASSWORD}@localhost:5432/meditech_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_NAME=MediTech System
DEBUG=False
CORS_ORIGINS=http://localhost,http://localhost:3000,http://localhost:8080
ORTHANC_URL=http://localhost:8042
ORTHANC_USERNAME=orthanc
ORTHANC_PASSWORD=orthanc
EOF

print_success "Archivos copiados"

# ==================== CONFIGURAR BACKEND ====================
print_info "Configurando backend Python..."

cd $INSTALL_DIR/backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

print_success "Backend configurado"

# ==================== CREAR SERVICIO SYSTEMD PARA BACKEND ====================
print_info "Creando servicio systemd para backend..."

cat > /etc/systemd/system/meditech-backend.service << EOF
[Unit]
Description=MediTech Backend API
After=network.target postgresql.service redis.service orthanc.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$INSTALL_DIR/backend/venv/bin"
ExecStart=$INSTALL_DIR/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable meditech-backend
print_success "Servicio backend creado"

# ==================== CONFIGURAR FRONTEND ====================
print_info "Configurando frontend React..."

# Instalar Node.js si no está instalado
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
fi

cd $INSTALL_DIR/frontend

# Instalar dependencias
npm install

# Crear build de producción
npm run build

print_success "Frontend compilado"

# ==================== CONFIGURAR NGINX ====================
print_info "Configurando Nginx..."

cat > /etc/nginx/sites-available/meditech << 'EOF'
server {
    listen 80;
    server_name localhost;

    # Frontend
    location / {
        root /opt/meditech/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Orthanc PACS
    location /orthanc/ {
        proxy_pass http://localhost:8042/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Archivos estáticos
    location /static/ {
        alias /opt/meditech/backend/static/;
    }
}
EOF

ln -sf /etc/nginx/sites-available/meditech /etc/nginx/sites-enabled/meditech
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx
systemctl enable nginx

print_success "Nginx configurado"

# ==================== INICIALIZAR BASE DE DATOS ====================
print_info "Inicializando base de datos..."

cd $INSTALL_DIR/backend
source venv/bin/activate

# Ejecutar migraciones (crear tablas)
python << 'PYTHON_EOF'
import sys
sys.path.insert(0, '/opt/meditech/backend')

from sqlalchemy import create_engine
from app.models.database import Base
import os
from dotenv import load_dotenv

load_dotenv('/opt/meditech/backend/app/.env')

engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.create_all(bind=engine)
print("Tablas creadas exitosamente")
PYTHON_EOF

print_success "Base de datos inicializada"

# ==================== INICIAR SERVICIOS ====================
print_info "Iniciando servicios..."

systemctl start meditech-backend
systemctl restart orthanc

print_success "Servicios iniciados"

# ==================== MOSTRAR INFORMACIÓN FINAL ====================
echo ""
echo "=============================================="
echo -e "${GREEN}  ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!${NC}"
echo "=============================================="
echo ""
echo "URLs de acceso:"
echo "  → Frontend: http://localhost"
echo "  → API Docs: http://localhost/api/docs"
echo "  → Orthanc PACS: http://localhost:8042"
echo ""
echo "Credenciales de Orthanc:"
echo "  Usuario: orthanc"
echo "  Contraseña: orthanc"
echo ""
echo "Contraseña de PostgreSQL:"
echo "  $DB_PASSWORD"
echo ""
echo "=============================================="
echo ""
print_info "Para crear el usuario ROOT, accede a:"
echo "  http://localhost/api/v1/auth/root/setup"
echo ""
echo "O ejecuta:"
echo "  cd $INSTALL_DIR/backend && source venv/bin/activate"
echo "  python scripts/init_db.py"
echo ""
echo "=============================================="
print_success "¡MediTech System listo para usar!"
echo ""
