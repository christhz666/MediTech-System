"""
API de Autenticación - MediTech System
Autor: Christhz 3.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.database import User, Role, Branch
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

router = APIRouter()

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== SCHEMAS ====================
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    branch_code: str


class RootSetup(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = "Administrador ROOT"
    branch_code: str = "MAIN01"
    branch_name: str = "Sucursal Principal"


# ==================== FUNCIONES AUXILIARES ====================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    to_encode.update({"type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


# ==================== ENDPOINTS ====================
@router.post("/root/setup", response_model=Token)
async def setup_root(root_data: RootSetup, db: Session = Depends(get_db)):
    """
    Configurar usuario SUPER_ROOT inicial.
    Solo funciona si no existe ningún usuario en el sistema.
    """
    # Verificar si ya existe algún usuario
    existing_user = db.query(User).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El sistema ya está configurado. Usa el login normal."
        )
    
    # Crear o buscar sucursal
    branch = db.query(Branch).filter(Branch.code == root_data.branch_code.upper()).first()
    if not branch:
        branch = Branch(
            code=root_data.branch_code.upper(),
            name=root_data.branch_name,
            active=True
        )
        db.add(branch)
        db.commit()
        db.refresh(branch)
    
    # Crear rol SUPER_ROOT si no existe
    role = db.query(Role).filter(Role.name == "SUPER_ROOT").first()
    if not role:
        role = Role(
            name="SUPER_ROOT",
            description="Acceso total al sistema",
            permissions='{"all": true}'
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    
    # Crear usuario ROOT
    user = User(
        username=root_data.username,
        email=root_data.email,
        password_hash=get_password_hash(root_data.password),
        full_name=root_data.full_name,
        role_id=role.id,
        branch_id=branch.id,
        active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generar tokens
    access_token = create_access_token(
        data={"sub": user.username, "role": role.name, "branch_id": branch.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "role": role.name}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": role.name,
            "branch_id": branch.id
        }
    }


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login de usuario.
    Devuelve access token y refresh token.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Actualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Obtener información del rol
    role = db.query(Role).filter(Role.id == user.role_id).first()
    
    # Generar tokens
    access_token = create_access_token(
        data={"sub": user.username, "role": role.name, "branch_id": user.branch_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "role": role.name}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": role.name,
            "branch_id": user.branch_id
        }
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Renovar access token usando refresh token.
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo"
            )
        
        role = db.query(Role).filter(Role.id == user.role_id).first()
        
        # Generar nuevo access token
        access_token = create_access_token(
            data={"sub": user.username, "role": role.name, "branch_id": user.branch_id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
