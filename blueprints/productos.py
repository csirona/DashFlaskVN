# blueprints/productos.py
from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
import json
from helpers import API_URL, login_required, get_headers

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

@productos_bp.route("/")
@login_required()
def listar():
    headers = get_headers()
    
    # Obtener productos (la API filtra por tenant automáticamente)
    resp = requests.get(f"{API_URL}/productos/", headers=headers)
    
    # === DEBUG: Imprimir la respuesta cruda ===
    print("=" * 50)
    print("🔍 STATUS CODE:", resp.status_code)
    print("🔍 RESPUESTA CRUDA (primeros 500 chars):", resp.text[:500])
    
    productos = resp.json() if resp.status_code == 200 else []
    
    # === DEBUG: Imprimir el primer producto con su impuesto ===
    if productos:
        print("🔍 PRIMER PRODUCTO COMPLETO:")
        print(json.dumps(productos[0], indent=2, default=str))
        
        # Verificar específicamente el campo impuesto
        if "impuesto" in productos[0]:
            print("🔍 IMPUESTO DEL PRIMER PRODUCTO:", productos[0]["impuesto"])
        else:
            print("🔍 NO HAY CAMPO 'impuesto' en el primer producto")
    else:
        print("🔍 NO HAY PRODUCTOS")
    
    # Obtener impuestos para el formulario
    resp_taxes = requests.get(f"{API_URL}/impuestos/", headers=headers)
    impuestos = resp_taxes.json() if resp_taxes.status_code == 200 else []
    
    # Determinar si el usuario puede crear/modificar (tiene tenant)
    perfil_resp = requests.get(f"{API_URL}/perfil", headers=headers)
    if perfil_resp.status_code == 200:
        perfil = perfil_resp.json()
        tiene_tenant = perfil.get("tenant_id") is not None
    else:
        tiene_tenant = False
    
    return render_template("productos.html",
                           productos=productos,
                           impuestos=impuestos,
                           tiene_tenant=tiene_tenant,
                           username=session.get("username"))


@productos_bp.route("/crear", methods=["POST"])
@login_required()
def crear():
    headers = get_headers()
    data = {
        "nombre": request.form["nombre"],
        "codigo": request.form.get("codigo") or None,  # ← NUEVO
        "descripcion": request.form.get("descripcion"),
        "precio": float(request.form["precio"]),
        "impuesto_id": int(request.form["impuesto_id"]) if request.form.get("impuesto_id") else None
    }
    
    print("🔍 CREANDO PRODUCTO:", data)
    
    resp = requests.post(f"{API_URL}/productos/", json=data, headers=headers)
    
    if resp.status_code != 201:
        error = resp.json().get("detail", "Error al crear producto")
        print("❌ ERROR:", error)
        # Redirigir con mensaje de error (puedes usar flash si lo prefieres)
    
    return redirect(url_for("productos.listar"))


@productos_bp.route("/editar/<int:producto_id>", methods=["POST"])
@login_required()
def editar(producto_id):
    headers = get_headers()
    data = {}
    
    # Campos de texto
    for field in ["nombre", "codigo", "descripcion"]:  # ← AÑADIDO "codigo"
        if request.form.get(field) is not None:
            data[field] = request.form[field] if request.form[field] != "" else None
    
    # Precio (numérico)
    if request.form.get("precio"):
        data["precio"] = float(request.form["precio"])
    
    # Impuesto (puede ser null)
    imp_id = request.form.get("impuesto_id")
    if imp_id is not None:
        data["impuesto_id"] = int(imp_id) if imp_id != "" else None
    
    print(f"🔍 EDITANDO PRODUCTO {producto_id}:", data)
    
    resp = requests.put(f"{API_URL}/productos/{producto_id}", json=data, headers=headers)
    
    if resp.status_code != 200:
        error = resp.json().get("detail", "Error al editar producto")
        print("❌ ERROR:", error)
    
    return redirect(url_for("productos.listar"))


@productos_bp.route("/eliminar/<int:producto_id>", methods=["POST"])
@login_required()
def eliminar(producto_id):
    headers = get_headers()
    requests.delete(f"{API_URL}/productos/{producto_id}", headers=headers)
    return redirect(url_for("productos.listar"))