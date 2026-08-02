# blueprints/clientes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
from helpers import API_URL, login_required, get_headers

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

CAMPOS_ORDENABLES = {
    "razon_social": lambda c: (c.get("razon_social") or "").lower(),
    "giro": lambda c: (c.get("giro") or "").lower(),
    "comuna": lambda c: (c.get("comuna") or "").lower(),
    "ciudad": lambda c: (c.get("ciudad") or "").lower(),
}


@clientes_bp.route("/")
@login_required()
def listar():
    headers = get_headers()
    resp = requests.get(f"{API_URL}/clientes/", headers=headers)
    clientes = resp.json() if resp.status_code == 200 else []

    # --- Leer filtros y orden desde la query string ---
    q = request.args.get("q", "").strip()
    ciudad_filtro = request.args.get("ciudad", "")
    sort = request.args.get("sort", "razon_social")
    order = request.args.get("order", "asc")

    if sort not in CAMPOS_ORDENABLES:
        sort = "razon_social"
    if order not in ("asc", "desc"):
        order = "asc"

    # Lista de ciudades disponibles para el select (antes de filtrar por texto)
    ciudades = sorted({c.get("ciudad") for c in clientes if c.get("ciudad")})

    # --- Aplicar filtros ---
    if q:
        q_lower = q.lower()
        clientes = [
            c for c in clientes
            if q_lower in (c.get("razon_social") or "").lower()
            or q_lower in (c.get("giro") or "").lower()
            or q_lower in (c.get("comuna") or "").lower()
        ]

    if ciudad_filtro:
        clientes = [c for c in clientes if c.get("ciudad") == ciudad_filtro]

    # --- Aplicar orden ---
    clientes.sort(key=CAMPOS_ORDENABLES[sort], reverse=(order == "desc"))

    return render_template(
        "clientes.html",
        clientes=clientes,
        username=session.get("username"),
        tenant_id=session.get("tenant_id"),
        ciudades=ciudades,
        q=q,
        ciudad_filtro=ciudad_filtro,
        sort=sort,
        order=order,
    )

@clientes_bp.route("/crear", methods=["POST"])
@login_required()
def crear():
    headers = get_headers()
    data = {
        "razon_social": request.form["razon_social"],
        "giro": request.form["giro"],
        "comuna": request.form["comuna"],
        "ciudad": request.form["ciudad"],
        "direccion": request.form["direccion"]
    }
    requests.post(f"{API_URL}/clientes", json=data, headers=headers)
    return redirect(url_for("clientes.listar"))

@clientes_bp.route("/editar/<int:cliente_id>", methods=["POST"])
@login_required()
def editar(cliente_id):
    headers = get_headers()
    data = {}
    # Solo envía los campos que vengan en el formulario (permite edición parcial)
    if request.form.get("razon_social"):
        data["razon_social"] = request.form["razon_social"]
    if request.form.get("giro"):
        data["giro"] = request.form["giro"]
    if request.form.get("comuna"):
        data["comuna"] = request.form["comuna"]
    if request.form.get("ciudad"):
        data["ciudad"] = request.form["ciudad"]
    if request.form.get("direccion"):
        data["direccion"] = request.form["direccion"]
    requests.put(f"{API_URL}/clientes/{cliente_id}", json=data, headers=headers)
    return redirect(url_for("clientes.listar"))

@clientes_bp.route("/eliminar/<int:cliente_id>", methods=["POST"])
@login_required()
def eliminar(cliente_id):
    headers = get_headers()
    requests.delete(f"{API_URL}/clientes/{cliente_id}", headers=headers)
    return redirect(url_for("clientes.listar"))