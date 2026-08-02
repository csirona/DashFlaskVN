# blueprints/productos.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests
from helpers import API_URL, login_required, get_headers

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

# Campos por los que se puede ordenar y cómo extraer su valor de cada producto
CAMPOS_ORDENABLES = {
    "id": lambda p: p.get("id") or 0,
    "codigo": lambda p: (p.get("codigo") or "").lower(),
    "nombre": lambda p: (p.get("nombre") or "").lower(),
    "precio": lambda p: p.get("precio") or 0,
}


def _extraer_error(resp, default="Ocurrió un error"):
    """Intenta extraer el mensaje de error del backend sin romper si no es JSON."""
    try:
        return resp.json().get("detail", default)
    except ValueError:
        return f"{default} (status {resp.status_code})"


@productos_bp.route("/")
@login_required()
def listar():
    headers = get_headers()

    resp = requests.get(f"{API_URL}/productos/", headers=headers)
    productos = resp.json() if resp.status_code == 200 else []

    resp_taxes = requests.get(f"{API_URL}/impuestos/", headers=headers)
    impuestos = resp_taxes.json() if resp_taxes.status_code == 200 else []

    perfil_resp = requests.get(f"{API_URL}/perfil", headers=headers)
    if perfil_resp.status_code == 200:
        perfil = perfil_resp.json()
        tiene_tenant = perfil.get("tenant_id") is not None
    else:
        tiene_tenant = False

    # Solo un admin global necesita filtrar por tenant
    tenants = []
    if not tiene_tenant:
        resp_tenants = requests.get(f"{API_URL}/tenants/", headers=headers)
        if resp_tenants.status_code == 200:
            tenants = resp_tenants.json()

    # --- Leer filtros y orden desde la query string ---
    q = request.args.get("q", "").strip()
    impuesto_filtro = request.args.get("impuesto_id", "")
    tenant_filtro = request.args.get("tenant_id", "")
    sort = request.args.get("sort", "nombre")
    order = request.args.get("order", "asc")

    if sort not in CAMPOS_ORDENABLES:
        sort = "nombre"
    if order not in ("asc", "desc"):
        order = "asc"

    # --- Aplicar filtros ---
    if q:
        q_lower = q.lower()
        productos = [
            p for p in productos
            if q_lower in (p.get("nombre") or "").lower()
            or q_lower in (p.get("codigo") or "").lower()
        ]

    if impuesto_filtro:
        if impuesto_filtro == "sin":
            productos = [p for p in productos if not p.get("impuesto")]
        else:
            productos = [
                p for p in productos
                if p.get("impuesto") and str(p["impuesto"].get("id")) == impuesto_filtro
            ]

    if tenant_filtro and not tiene_tenant:
        if tenant_filtro == "sin":
            productos = [p for p in productos if not p.get("tenant_id")]
        else:
            productos = [p for p in productos if str(p.get("tenant_id")) == tenant_filtro]

    # --- Aplicar orden ---
    productos.sort(key=CAMPOS_ORDENABLES[sort], reverse=(order == "desc"))

    return render_template(
        "productos.html",
        productos=productos,
        impuestos=impuestos,
        tenants=tenants,
        tiene_tenant=tiene_tenant,
        username=session.get("username"),
        q=q,
        impuesto_filtro=impuesto_filtro,
        tenant_filtro=tenant_filtro,
        sort=sort,
        order=order,
    )


@productos_bp.route("/crear", methods=["POST"])
@login_required()
def crear():
    headers = get_headers()
    data = {
        "nombre": request.form["nombre"],
        "codigo": request.form.get("codigo") or None,
        "descripcion": request.form.get("descripcion") or None,
        "precio": float(request.form["precio"]),
        "impuesto_id": int(request.form["impuesto_id"]) if request.form.get("impuesto_id") else None,
    }

    resp = requests.post(f"{API_URL}/productos/", json=data, headers=headers)

    if resp.status_code != 201:
        flash(_extraer_error(resp, "Error al crear producto"), "danger")
    else:
        flash("Producto creado correctamente", "success")

    return redirect(url_for("productos.listar"))


@productos_bp.route("/editar/<int:producto_id>", methods=["POST"])
@login_required()
def editar(producto_id):
    headers = get_headers()
    data = {}

    for field in ["nombre", "codigo", "descripcion"]:
        if request.form.get(field) is not None:
            data[field] = request.form[field] if request.form[field] != "" else None

    if request.form.get("precio"):
        data["precio"] = float(request.form["precio"])

    imp_id = request.form.get("impuesto_id")
    if imp_id is not None:
        data["impuesto_id"] = int(imp_id) if imp_id != "" else None

    resp = requests.put(f"{API_URL}/productos/{producto_id}", json=data, headers=headers)

    if resp.status_code != 200:
        flash(_extraer_error(resp, "Error al editar producto"), "danger")
    else:
        flash("Producto actualizado correctamente", "success")

    return redirect(url_for("productos.listar"))


@productos_bp.route("/eliminar/<int:producto_id>", methods=["POST"])
@login_required()
def eliminar(producto_id):
    headers = get_headers()
    resp = requests.delete(f"{API_URL}/productos/{producto_id}", headers=headers)

    if resp.status_code not in (200, 204):
        flash(_extraer_error(resp, "Error al eliminar producto"), "danger")
    else:
        flash("Producto eliminado correctamente", "success")

    return redirect(url_for("productos.listar"))