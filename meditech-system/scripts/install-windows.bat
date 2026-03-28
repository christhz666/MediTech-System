@echo off
setlocal EnableDelayedExpansion

:: ==========================================
:: MediTech System - Windows Auto Installer
:: Desarrollado por Christhz 3.0
:: Instalación 100% Automática
:: ==========================================

echo.
echo ==========================================
echo   MEDI TECH SYSTEM - INSTALADOR WINDOWS
echo   Version: 3.0 (Auto Install)
echo ==========================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Este script requiere permisos de Administrador.
    echo Haz clic derecho y selecciona "Ejecutar como administrador".
    pause
    exit /b 1
)

:: Configuración
set "PROJECT_ROOT=%~dp0.."
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
set "VENV_DIR=%BACKEND_DIR%\venv"
set "DB_NAME=meditech_db"
set "DB_USER=meditech_user"
set "DB_PASS=!RANDOM!!RANDOM!!RANDOM!"
set "PG_DATA=C:\Program Files\PostgreSQL\16\data"

echo [*] Iniciando instalación automática...
echo.

:: ==========================================
:: 1. INSTALACIÓN DE DEPENDENCIAS CON WINGET
:: ==========================================
echo [PASO 1] Verificando e instalando dependencias del sistema...

:: Verificar Winget
where winget >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Winget no encontrado. Por favor actualiza Windows Store.
    pause
    exit /b 1
)

:: Instalar Python si no existe
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [*] Instalando Python 3.11...
    winget install -e --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
) else (
    echo [*] Python ya instalado.
)

:: Instalar Node.js si no existe
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [*] Instalando Node.js LTS...
    winget install -e --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
) else (
    echo [*] Node.js ya instalado.
)

:: Instalar PostgreSQL si no existe
where psql >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [*] Instalando PostgreSQL 16...
    winget install -e --id PostgreSQL.PostgreSQL.16 --silent --accept-package-agreements --accept-source-agreements
    echo [*] Esperando a que PostgreSQL se instale completamente...
    timeout /t 30 /nobreak >nul
) else (
    echo [*] PostgreSQL ya instalado.
)

:: Instalar Git si no existe
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [*] Instalando Git...
    winget install -e --id Git.Git --silent --accept-package-agreements --accept-source-agreements
) else (
    echo [*] Git ya instalado.
)

:: Actualizar PATH para esta sesión
set "PATH=C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%PATH%"
set "PATH=C:\Program Files\nodejs;%PATH%"
set "PATH=C:\Program Files\PostgreSQL\16\bin;%PATH%"
set "PATH=C:\Program Files\Git\cmd;%PATH%"

echo.
echo [PASO 2] Configurando Base de Datos PostgreSQL...

:: Crear usuario y base de datos
echo [*] Creando usuario de base de datos '%DB_USER%'...
psql -U postgres -c "SELECT 1 FROM pg_roles WHERE rolname='%DB_USER%'" | findstr "1" >nul
if %ERRORLEVEL% neq 0 (
    psql -U postgres -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASS%';"
) else (
    echo [*] Usuario ya existe, actualizando contraseña...
    psql -U postgres -c "ALTER USER %DB_USER% WITH PASSWORD '%DB_PASS%';"
)

echo [*] Creando base de datos '%DB_NAME%'...
psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname='%DB_NAME%'" | findstr "1" >nul
if %ERRORLEVEL% neq 0 (
    psql -U postgres -c "CREATE DATABASE %DB_NAME% OWNER %DB_USER%;"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"
) else (
    echo [*] Base de datos ya existe.
)

:: Habilitar extensión UUID
psql -U %DB_USER% -d %DB_NAME% -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

echo.
echo [PASO 3] Preparando entorno Python...

cd /d "%BACKEND_DIR%"

:: Crear entorno virtual
if not exist "%VENV_DIR%" (
    echo [*] Creando entorno virtual...
    python -m venv venv
)

:: Activar entorno
call "%VENV_DIR%\Scripts\activate.bat"

:: Actualizar pip e instalar dependencias
echo [*] Instalando dependencias de Python...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo.
echo [PASO 4] Preparando entorno Node.js...

cd /d "%FRONTEND_DIR%"

:: Instalar dependencias frontend
if not exist "node_modules" (
    echo [*] Instalando dependencias de Node.js (esto puede tardar)...
    call npm install --loglevel=error
) else (
    echo [*] Dependencias de Node.js ya instaladas.
)

echo.
echo [PASO 5] Inicializando Base de Datos...

cd /d "%BACKEND_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

:: Configurar variables de entorno para inicialización
set "DATABASE_URL=postgresql://%DB_USER%:%DB_PASS%@localhost:5432/%DB_NAME%"
set "SECRET_KEY=supersecretkey_windows_%RANDOM%%RANDOM%"

:: Ejecutar script de inicialización
echo [*] Creando usuario SUPER_ROOT y datos iniciales...
python scripts/init_db.py --auto --db-url "%DATABASE_URL%" --secret "%SECRET_KEY%"

:: Guardar credenciales en archivo
echo.
echo ==========================================
echo   INSTALACION COMPLETADA
echo ==========================================
echo.
echo Credenciales guardadas en: %PROJECT_ROOT%\credentials.txt
echo.
(
    echo ==========================================
    echo   MEDI TECH SYSTEM - CREDENCIALES
    echo ==========================================
    echo.
    echo Database URL: %DATABASE_URL%
    echo Secret Key: %SECRET_KEY%
    echo.
    echo USUARIO SUPER_ROOT:
    echo Email: superroot@meditech.local
    echo Password: Admin123!
    echo.
    echo ==========================================
) > "%PROJECT_ROOT%\credentials.txt"

type "%PROJECT_ROOT%\credentials.txt"

echo.
echo [PASO 6] ¿Deseas iniciar el sistema ahora?
set /p START_NOW="Presiona 'S' para iniciar o cualquier otra tecla para salir: "

if /i "%START_NOW%"=="S" (
    echo.
    echo [*] Iniciando servicios...
    
    :: Iniciar Backend
    start "MediTech Backend" cmd /k "cd /d %BACKEND_DIR% && call venv\Scripts\activate.bat && set DATABASE_URL=%DATABASE_URL% && set SECRET_KEY=%SECRET_KEY% && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    :: Iniciar Frontend
    start "MediTech Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"
    
    echo.
    echo ==========================================
    echo   SISTEMA EN EJECUCION
    echo ==========================================
    echo.
    echo   Backend API: http://localhost:8000
    echo   Docs Swagger: http://localhost:8000/docs
    echo   Frontend: http://localhost:5173
    echo.
    echo   Abre tu navegador en http://localhost:5173
    echo   Para detener: Cierra las ventanas emergentes.
    echo.
) else (
    echo.
    echo [*] Instalación completada. Puedes iniciar el sistema manualmente con:
    echo     cd backend && venv\Scripts\activate && uvicorn app.main:app --reload
    echo     cd frontend && npm run dev
)

pause
