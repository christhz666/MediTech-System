"""
Modelos de Base de Datos - MediTech System v3.0
Autor: Christhz 3.0
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class RoleType(str, enum.Enum):
    SUPER_ROOT = "super_root"
    ADMIN = "admin"
    RECEPCION = "recepcion"
    DOCTOR = "doctor"
    LABORATORIO = "laboratorio"
    RADIOLOGO = "radiologo"
    CONTABILIDAD = "contabilidad"


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    PAYPAL = "paypal"
    INSURANCE = "insurance"


# ==================== SUCURSALES ====================
class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    phone = Column(String(20))
    email = Column(String(100))
    logo_url = Column(String(255))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    users = relationship("User", back_populates="branch")
    patients = relationship("Patient", back_populates="branch")
    invoices = relationship("Invoice", back_populates="branch")
    studies_catalog = relationship("StudyCatalog", back_populates="branch")


# ==================== ROLES ====================
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(Text)  # JSON con permisos
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    users = relationship("User", back_populates="role")


# ==================== USUARIOS ====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    role = relationship("Role", back_populates="users")
    branch = relationship("Branch", back_populates="users")


# ==================== PACIENTES ====================
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    id_number = Column(String(20), index=True)  # Cédula, puede ser NULL para menores
    date_of_birth = Column(DateTime)
    gender = Column(String(10))
    blood_type = Column(String(5))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(255))
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(20))
    medical_history = Column(Text)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    branch = relationship("Branch", back_populates="patients")
    invoices = relationship("Invoice", back_populates="patient")


# ==================== CATALOGO DE ESTUDIOS ====================
class StudyCatalog(Base):
    __tablename__ = "study_catalog"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    price = Column(Float, nullable=False)
    category = Column(String(50))  # laboratorio, radiologia, etc.
    requires_sample = Column(Boolean, default=False)
    requires_fasting = Column(Boolean, default=False)
    turnaround_time_hours = Column(Integer)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    branch = relationship("Branch", back_populates="studies_catalog")


# ==================== FACTURAS ====================
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_code = Column(String(10), unique=True, nullable=False, index=True)  # ID 4-5 digitos
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Totales
    subtotal = Column(Float, nullable=False, default=0)
    insurance_coverage_percent = Column(Float, default=0)
    insurance_amount = Column(Float, default=0)
    patient_amount = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False, default=0)
    amount_paid = Column(Float, default=0)
    balance = Column(Float, nullable=False, default=0)
    
    # Estado y metodo
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.PENDING)
    payment_method = Column(SQLEnum(PaymentMethod))
    
    # Codigos unicos
    barcode = Column(String(50), unique=True, index=True)
    qr_code = Column(String(255), unique=True)
    
    # Integraciones
    orthanc_study_uid = Column(String(100))  # Para PACS
    openelis_order_id = Column(String(50))   # Para LIS
    
    # Seguros
    insurance_name = Column(String(100))
    insurance_policy_number = Column(String(50))
    
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True))

    # Relaciones
    branch = relationship("Branch", back_populates="invoices")
    patient = relationship("Patient", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="invoice", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('branch_id', 'invoice_code', name='uq_branch_invoice_code'),
    )


# ==================== ITEMS DE FACTURA ====================
class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    study_catalog_id = Column(Integer, ForeignKey("study_catalog.id"))
    study_name = Column(String(100), nullable=False)  # Copia del nombre
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    invoice = relationship("Invoice", back_populates="items")


# ==================== PAGOS ====================
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    reference = Column(String(100))  # Numero transaccion, cheque, etc.
    notes = Column(Text)
    processed_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    invoice = relationship("Invoice", back_populates="payments")


# ==================== RESULTADOS ====================
class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    invoice_item_id = Column(Integer, ForeignKey("invoice_items.id"))
    
    # Tipo de resultado
    result_type = Column(String(20))  # laboratory, radiology
    
    # Contenido
    data = Column(Text)  # JSON con resultados estructurados
    file_path = Column(String(255))  # PDF u otro archivo
    dicom_study_uid = Column(String(100))  # Referencia a Orthanc
    
    # Estados
    status = Column(String(20), default="pending")  # pending, completed, validated
    validated_by = Column(Integer, ForeignKey("users.id"))
    validated_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    invoice = relationship("Invoice", back_populates="results")


# ==================== AUDITORIA ====================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)
    table_name = Column(String(50))
    record_id = Column(Integer)
    old_values = Column(Text)  # JSON
    new_values = Column(Text)  # JSON
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
