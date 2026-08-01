# schemas.py
from pydantic import BaseModel
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int = 0
    activo: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    activo: Optional[bool] = None

class ProductoOut(ProductoBase):
    id: int

    class Config:
        orm_mode = True


# schemas.py (añadir al final o donde corresponda)

class TenantOut(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

# Modifica ProductoResponse (reemplaza la definición anterior)
class ProductoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    precio: float
    tenant_id: int
    impuesto: Optional[ImpuestoResponse] = None
    tenant: Optional[TenantOut] = None   # <-- NUEVO

    class Config:
        from_attributes = True

class TenantUpdate(BaseModel):
    razon_social: Optional[str] = None
    rut: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None

class TenantResponse(BaseModel):
    id: int
    nombre: str
    razon_social: Optional[str] = None
    rut: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True