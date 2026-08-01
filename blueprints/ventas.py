# blueprints/ventas.py
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import requests
import json
from helpers import API_URL, login_required, get_headers
from datetime import datetime

ventas_bp = Blueprint("ventas", __name__, url_prefix="/ventas")


@ventas_bp.route("/")
@login_required()
def listar():
    headers = get_headers()
    
    # Obtener ventas
    resp_ventas = requests.get(f"{API_URL}/ventas/", headers=headers)
    ventas = resp_ventas.json() if resp_ventas.status_code == 200 else []
    
    # Obtener clientes para el modal de nueva venta
    resp_clientes = requests.get(f"{API_URL}/clientes/", headers=headers)
    clientes = resp_clientes.json() if resp_clientes.status_code == 200 else []
    
    # Obtener productos (solo para referencias, ya no para select)
    resp_productos = requests.get(f"{API_URL}/productos/", headers=headers)
    productos = resp_productos.json() if resp_productos.status_code == 200 else []
    
    # Obtener impuestos
    resp_impuestos = requests.get(f"{API_URL}/impuestos/", headers=headers)
    impuestos = resp_impuestos.json() if resp_impuestos.status_code == 200 else []
    
    return render_template(
        "ventas.html",
        ventas=ventas,
        clientes=clientes,
        productos=productos,
        impuestos=impuestos,
        username=session.get("username"),
        tenant_id=session.get("tenant_id")
    )


@ventas_bp.route("/api/productos/buscar")
@login_required()
def buscar_productos():
    """
    Endpoint intermedio para búsqueda AJAX de productos.
    El frontend llama aquí → Flask consulta a FastAPI → Devuelve JSON formateado.
    """
    q = request.args.get('q', '').strip()
    
    # Validación: mínimo 2 caracteres
    if len(q) < 2:
        return jsonify([])
    
    headers = get_headers()
    
    try:
        # Llamar al endpoint de búsqueda de FastAPI
        resp = requests.get(
            f"{API_URL}/productos/buscar/",
            params={"q": q},
            headers=headers,
            timeout=5
        )
        
        if resp.status_code == 200:
            productos = resp.json()
        else:
            print(f"⚠️ API respondió {resp.status_code}: {resp.text}")
            return jsonify([])
        
        # Formatear para el frontend
        resultado = []
        for p in productos:
            impuesto_info = p.get('impuesto') or {}
            resultado.append({
        'id': p.get('id'),
        'nombre': p.get('nombre', ''),
        'codigo': p.get('codigo', ''),
        'precio': p.get('precio', 0),
        'impuesto_id': impuesto_info.get('id'),
        'impuesto_tasa': impuesto_info.get('tasa', 0),
        'impuesto_nombre': impuesto_info.get('descripcion', '')
    })
        
        return jsonify(resultado)
        
    except requests.exceptions.Timeout:
        print("❌ Timeout al buscar productos en la API")
        return jsonify({"error": "Tiempo de espera agotado"}), 504
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión con la API: {e}")
        return jsonify({"error": "Servicio no disponible"}), 503
        
    except Exception as e:
        print(f"❌ Error inesperado en búsqueda: {e}")
        return jsonify({"error": str(e)}), 500


@ventas_bp.route("/crear", methods=["POST"])
@login_required()
def crear():
    headers = get_headers()
    
    # Construir el JSON para la API
    data = {
        "cliente_id": int(request.form["cliente_id"]),
        "tipo_comprobante": request.form.get("tipo_comprobante", "boleta"),
        "observaciones": request.form.get("observaciones", ""),
        "detalles": []
    }
    
    # Procesar los detalles (vienen como arrays del formulario)
    productos_ids = request.form.getlist("producto_id[]")
    cantidades = request.form.getlist("cantidad[]")
    precios = request.form.getlist("precio_unitario[]")
    impuestos_esp_id = request.form.getlist("impuesto_esp_id[]")
    
    for i in range(len(productos_ids)):
        if productos_ids[i]:  # solo si hay producto seleccionado
            detalle = {
                "producto_id": int(productos_ids[i]),
                "cantidad": float(cantidades[i]),
                "precio_unitario": float(precios[i]),
                "descuento": 0.0
            }
            # Agregar impuesto específico si existe
            if i < len(impuestos_esp_id) and impuestos_esp_id[i]:
                detalle["impuesto_id"] = int(impuestos_esp_id[i])
            else:
                detalle["impuesto_id"] = None
            
            data["detalles"].append(detalle)
    
    # Enviar a la API
    resp = requests.post(f"{API_URL}/ventas/", json=data, headers=headers)
    
    if resp.status_code != 201:
        error_msg = resp.json().get("detail", "Error al crear venta")
        flash(error_msg, "danger")
    else:
        flash("Venta creada exitosamente", "success")
    
    return redirect(url_for("ventas.listar"))


@ventas_bp.route("/anular/<int:venta_id>", methods=["POST"])
@login_required()
def anular(venta_id):
    headers = get_headers()
    resp = requests.put(f"{API_URL}/ventas/{venta_id}/anular", headers=headers)
    
    if resp.status_code == 200:
        flash("Venta anulada exitosamente", "success")
    else:
        error_msg = resp.json().get("detail", "Error al anular venta")
        flash(error_msg, "danger")
    
    return redirect(url_for("ventas.listar"))