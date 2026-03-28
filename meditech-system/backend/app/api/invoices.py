"""
API de Facturación - MediTech System (Completa con lógica de negocio)
Autor: Christhz 3.0
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os
import random
import string
import qrcode
import barcode
from io import BytesIO
import base64
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.database import (
    Invoice, InvoiceItem, Patient, Branch, StudyCatalog, 
    InvoiceStatus, PaymentMethod, Result, Payment
)
from pydantic import BaseModel, Field
from decimal import Decimal

router = APIRouter()


# ==================== SCHEMAS ====================
class InvoiceItemCreate(BaseModel):
    study_catalog_id: Optional[int] = None
    study_name: str
    quantity: int = 1
    unit_price: float


class InvoiceCreate(BaseModel):
    patient_id: int
    branch_id: int
    user_id: int
    items: List[InvoiceItemCreate]
    insurance_name: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_coverage_percent: float = 0.0
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_code: str
    patient_id: int
    branch_id: int
    total: float
    amount_paid: float
    balance: float
    status: str
    barcode: str
    qr_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== FUNCIONES AUXILIARES ====================
def generate_invoice_code(branch_id: int, db: Session) -> str:
    """Generar ID único de 4-5 dígitos por sucursal"""
    while True:
        code = str(random.randint(1000, 99999))
        # Verificar que no exista en esta sucursal
        existing = db.query(Invoice).filter(
            Invoice.invoice_code == code,
            Invoice.branch_id == branch_id
        ).first()
        if not existing:
            return code


def generate_barcode(code: str) -> str:
    """Generar código de barras Code128"""
    try:
        bc = barcode.get('code128', code, writer=barcode.writer.ImageWriter())
        buffer = BytesIO()
        bc.write(buffer)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    except:
        return code


def generate_qr_code(data: str) -> str:
    """Generar código QR"""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    except:
        return data


# ==================== ENDPOINTS ====================
@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_data: InvoiceCreate, db: Session = Depends(get_db)):
    """
    Crear nueva factura con estudios.
    Genera automáticamente ID único, código de barras y QR.
    """
    # Verificar paciente y sucursal
    patient = db.query(Patient).filter(Patient.id == invoice_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    branch = db.query(Branch).filter(Branch.id == invoice_data.branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    
    # Generar código único de factura
    invoice_code = generate_invoice_code(invoice_data.branch_id, db)
    
    # Calcular totales
    subtotal = sum(item.unit_price * item.quantity for item in invoice_data.items)
    insurance_amount = subtotal * (invoice_data.insurance_coverage_percent / 100)
    patient_amount = subtotal - insurance_amount
    
    # Crear factura
    db_invoice = Invoice(
        invoice_code=invoice_code,
        patient_id=invoice_data.patient_id,
        branch_id=invoice_data.branch_id,
        user_id=invoice_data.user_id,
        subtotal=subtotal,
        insurance_coverage_percent=invoice_data.insurance_coverage_percent,
        insurance_amount=insurance_amount,
        patient_amount=patient_amount,
        total=subtotal,
        amount_paid=0,
        balance=patient_amount,
        status=InvoiceStatus.PENDING,
        barcode=invoice_code,
        qr_code=f"MEDITECH-{invoice_code}-{invoice_data.patient_id}",
        insurance_name=invoice_data.insurance_name,
        insurance_policy_number=invoice_data.insurance_policy_number,
        notes=invoice_data.notes
    )
    
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    # Crear items
    for item_data in invoice_data.items:
        db_item = InvoiceItem(
            invoice_id=db_invoice.id,
            study_catalog_id=item_data.study_catalog_id,
            study_name=item_data.study_name,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_data.unit_price * item_data.quantity
        )
        db.add(db_item)
    
    db.commit()
    
    # Generar códigos visuales
    db_invoice.barcode = generate_barcode(invoice_code)
    db_invoice.qr_code = generate_qr_code(db_invoice.qr_code)
    db.commit()
    
    return db_invoice


@router.get("/search/{term}")
async def search_invoice(term: str, db: Session = Depends(get_db)):
    """
    Buscar factura por ID, código de barras o QR.
    """
    # Intentar buscar por invoice_code
    invoice = db.query(Invoice).filter(Invoice.invoice_code == term).first()
    
    if not invoice:
        # Buscar por barcode
        invoice = db.query(Invoice).filter(Invoice.barcode.like(f"%{term}%")).first()
    
    if not invoice:
        # Buscar por QR
        invoice = db.query(Invoice).filter(Invoice.qr_code.like(f"%{term}%")).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return {
        "invoice": invoice,
        "items": invoice.items,
        "patient": invoice.patient,
        "results_available": len(invoice.results) > 0 if invoice.results else False
    }


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Obtener detalles completos de una factura"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return {
        "invoice": invoice,
        "items": invoice.items,
        "payments": invoice.payments,
        "patient": invoice.patient
    }


@router.post("/{invoice_id}/pay")
async def register_payment(
    invoice_id: int,
    amount: float,
    payment_method: str,
    reference: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Registrar pago de factura"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
    
    # Registrar pago
    payment = Payment(
        invoice_id=invoice_id,
        amount=amount,
        payment_method=PaymentMethod(payment_method),
        reference=reference
    )
    db.add(payment)
    
    # Actualizar estado de factura
    invoice.amount_paid += amount
    invoice.balance -= amount
    
    if invoice.balance <= 0:
        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.utcnow()
        invoice.balance = 0
    elif invoice.amount_paid > 0:
        invoice.status = InvoiceStatus.PARTIAL
    
    db.commit()
    
    return {
        "message": "Pago registrado exitosamente",
        "balance_remaining": invoice.balance,
        "status": invoice.status.value
    }


@router.get("/{invoice_id}/results")
async def get_results(invoice_id: int, db: Session = Depends(get_db)):
    """
    Obtener resultados de la factura.
    Solo si está completamente pagada.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Verificar si está pagada
    if invoice.status != InvoiceStatus.PAID:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "La factura tiene saldo pendiente",
                "balance": invoice.balance,
                "paid": invoice.amount_paid,
                "total": invoice.total,
                "action_required": "Por favor cancele el saldo pendiente para retirar los resultados"
            }
        )
    
    results = db.query(Result).filter(Result.invoice_id == invoice_id).all()
    
    return {
        "invoice": invoice,
        "results": results,
        "can_download": True
    }


@router.get("/patient/{patient_id}/history")
async def get_patient_invoices(patient_id: int, db: Session = Depends(get_db)):
    """Obtener todas las facturas de un paciente (historial completo)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    invoices = db.query(Invoice).filter(
        Invoice.patient_id == patient_id
    ).order_by(Invoice.created_at.desc()).all()
    
    return {
        "patient": patient,
        "total_invoices": len(invoices),
        "invoices": [
            {
                "id": inv.id,
                "invoice_code": inv.invoice_code,
                "total": inv.total,
                "status": inv.status.value,
                "created_at": inv.created_at,
                "items_count": len(inv.items)
            }
            for inv in invoices
        ]
    }
