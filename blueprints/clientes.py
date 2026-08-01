# blueprints/clientes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
from helpers import API_URL, login_required, get_headers

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

@clientes_bp.route("/")
@login_required()
def listar():
    headers = get_headers()
    resp = requests.get(f"{API_URL}/clientes/", headers=headers)   # nota la barra final
    clientes = resp.json() if resp.status_code == 200 else []
    return render_template(
        "clientes.html",
        clientes=clientes,
        username=session.get("username"),
        tenant_id=session.get("tenant_id")   # <-- nuevo
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