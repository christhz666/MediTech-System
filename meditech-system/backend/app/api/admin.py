"""
API de Administración - MediTech System
Autor: Christhz 3.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.database import Branch, Role, User
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== SCHEMAS ====================
class BranchCreate(BaseModel):
    code: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None


class BranchResponse(BaseModel):
    id: int
    code: str
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    logo_url: Optional[str]
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    branch_id: Optional[int] = None
    permissions: str = '{}'


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role_id: int
    branch_id: int


# ==================== ENDPOINTS SUCURSALES ====================
@router.post("/branches", response_model=BranchResponse)
async def create_branch(branch: BranchCreate, db: Session = Depends(get_db)):
    """Crear nueva sucursal"""
    # Verificar que el código no exista
    existing = db.query(Branch).filter(Branch.code == branch.code.upper()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una sucursal con este código"
        )
    
    db_branch = Branch(**branch.model_dump(), code=branch.code.upper())
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    
    return db_branch


@router.get("/branches", response_model=List[BranchResponse])
async def list_branches(db: Session = Depends(get_db)):
    """Listar todas las sucursales activas"""
    branches = db.query(Branch).filter(Branch.active == True).all()
    return branches


# ==================== ENDPOINTS ROLES ====================
@router.post("/roles")
async def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """Crear nuevo rol"""
    existing = db.query(Role).filter(Role.name == role.name.upper()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un rol con este nombre"
        )
    
    db_role = Role(
        name=role.name.upper(),
        description=role.description,
        branch_id=role.branch_id,
        permissions=role.permissions
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    
    return {"message": "Rol creado exitosamente", "role_id": db_role.id}


@router.get("/roles")
async def list_roles(db: Session = Depends(get_db)):
    """Listar todos los roles"""
    roles = db.query(Role).all()
    return roles


# ==================== ENDPOINTS USUARIOS ====================
@router.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Crear nuevo usuario"""
    # Verificar username único
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está en uso"
        )
    
    # Verificar email único
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar que rol y sucursal existan
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    branch = db.query(Branch).filter(Branch.id == user.branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    
    # Crear usuario
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=pwd_context.hash(user.password),
        full_name=user.full_name,
        role_id=user.role_id,
        branch_id=user.branch_id,
        active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "message": "Usuario creado exitosamente",
        "user_id": db_user.id,
        "username": db_user.username
    }


@router.get("/users")
async def list_users(
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Listar usuarios (opcionalmente por sucursal)"""
    query = db.query(User)
    if branch_id:
        query = query.filter(User.branch_id == branch_id)
    
    users = query.all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.name if u.role else None,
            "branch": u.branch.name if u.branch else None,
            "active": u.active
        }
        for u in users
    ]
