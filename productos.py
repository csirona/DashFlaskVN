# productos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Producto
from schemas import ProductoCreate, ProductoUpdate, ProductoOut
from auth import get_current_user   # tu dependencia de autenticación

router = APIRouter(prefix="/productos", tags=["productos"])

# Verifica que el usuario sea admin
def admin_only(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores")
    return current_user

# Listar todos los productos
@router.get("/", response_model=list[ProductoOut])
def listar(db: Session = Depends(get_db), user=Depends(admin_only)):
    return db.query(Producto).all()

# Obtener un producto por ID
@router.get("/{producto_id}", response_model=ProductoOut)
def obtener(producto_id: int, db: Session = Depends(get_db), user=Depends(admin_only)):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod

# Crear producto
@router.post("/", response_model=ProductoOut, status_code=201)
def crear(producto: ProductoCreate, db: Session = Depends(get_db), user=Depends(admin_only)):
    nuevo = Producto(**producto.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Actualizar producto
@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar(producto_id: int, datos: ProductoUpdate, db: Session = Depends(get_db), user=Depends(admin_only)):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(prod, key, value)
    db.commit()
    db.refresh(prod)
    return prod

# Eliminar producto
@router.delete("/{producto_id}", status_code=204)
def eliminar(producto_id: int, db: Session = Depends(get_db), user=Depends(admin_only)):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(prod)
    db.commit()
    return