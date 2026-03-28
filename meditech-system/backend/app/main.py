"""
MediTech System - Main Application
Autor: Christhz 3.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="MediTech System API",
    description="Sistema Integral de Gestión Médica",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers
from app.api import auth, patients, invoices, admin

# Incluir routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Pacientes"])
app.include_router(invoices.router, prefix="/api/v1/invoices", tags=["Facturación"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administración"])

@app.get("/")
async def root():
    return {
        "message": "MediTech System v3.0",
        "author": "Christhz 3.0",
        "docs": "/api/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
