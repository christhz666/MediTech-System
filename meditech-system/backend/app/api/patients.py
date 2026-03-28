"""
API de Pacientes - MediTech System
Autor: Christhz 3.0
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.database import Patient, Branch, Invoice
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()


# ==================== SCHEMAS ====================
class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    id_number: Optional[str] = Field(None, max_length=20)  # NULL para menores
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None
    branch_id: int


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    id_number: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    blood_type: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    branch_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================
@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Registrar nuevo paciente.
    La cédula es opcional (para menores de edad).
    """
    # Verificar que la sucursal existe
    branch = db.query(Branch).filter(Branch.id == patient.branch_id).first()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )
    
    # Verificar si ya existe paciente con misma cédula en la sucursal
    if patient.id_number and patient.id_number.upper() != "MENOR":
        existing = db.query(Patient).filter(
            Patient.id_number == patient.id_number.upper(),
            Patient.branch_id == patient.branch_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un paciente con esta cédula en esta sucursal"
            )
    
    # Crear paciente
    db_patient = Patient(
        **patient.model_dump(),
        id_number=patient.id_number.upper() if patient.id_number else None
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Listar pacientes con paginación.
    """
    query = db.query(Patient)
    
    if branch_id:
        query = query.filter(Patient.branch_id == branch_id)
    
    patients = query.order_by(Patient.last_name, Patient.first_name).offset(skip).limit(limit).all()
    return patients


@router.get("/search")
async def search_patients(
    q: str = Query(..., min_length=2),
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Buscar pacientes por nombre, apellido o cédula.
    """
    query = db.query(Patient)
    
    if branch_id:
        query = query.filter(Patient.branch_id == branch_id)
    
    # Búsqueda flexible
    search_term = f"%{q.lower()}%"
    patients = query.filter(
        (Patient.first_name.ilike(search_term)) |
        (Patient.last_name.ilike(search_term)) |
        (Patient.id_number.ilike(search_term) if Patient.id_number else False)
    ).order_by(Patient.last_name, Patient.first_name).limit(50).all()
    
    return patients


@router.get("/{patient_id}")
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Obtener detalles de un paciente específico.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar información de un paciente.
    """
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Actualizar campos
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "id_number" and value:
            value = value.upper()
        setattr(db_patient, field, value)
    
    db_patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.get("/{patient_id}/history")
async def get_patient_history(patient_id: int, db: Session = Depends(get_db)):
    """
    Obtener historial completo de un paciente (todas sus facturas y estudios).
    Ordenado del más reciente al más antiguo.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Obtener todas las facturas del paciente
    invoices = db.query(Invoice).filter(
        Invoice.patient_id == patient_id
    ).order_by(Invoice.created_at.desc()).all()
    
    return {
        "patient": patient,
        "total_invoices": len(invoices),
        "invoices": invoices
    }
