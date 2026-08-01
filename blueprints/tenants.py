# blueprints/tenants.py
from flask import Blueprint, render_template, request, redirect, url_for
import requests
from helpers import API_URL, login_required, get_headers

tenants_bp = Blueprint("tenants", __name__, url_prefix="/tenants")

@tenants_bp.route("/")
@login_required(role="admin")   # podrías ser más restrictivo aquí
def listar():
    headers = get_headers()
    resp = requests.get(f"{API_URL}/tenants/", headers=headers)
    tenants = resp.json() if resp.status_code == 200 else []
    return render_template("tenants.html", tenants=tenants)

@tenants_bp.route("/crear", methods=["POST"])
@login_required(role="admin")
def crear():
    headers = get_headers()
    data = {"nombre": request.form["nombre"]}
    requests.post(f"{API_URL}/tenants/", json=data, headers=headers)
    return redirect(url_for("tenants.listar"))

@tenants_bp.route("/editar/<int:tenant_id>", methods=["POST"])
@login_required(role="admin")
def editar(tenant_id):
    headers = get_headers()
    data = {"nombre": request.form["nombre"]}
    requests.put(f"{API_URL}/tenants/{tenant_id}", json=data, headers=headers)
    return redirect(url_for("tenants.listar"))

@tenants_bp.route("/eliminar/<int:tenant_id>", methods=["POST"])
@login_required(role="admin")
def eliminar(tenant_id):
    headers = get_headers()
    requests.delete(f"{API_URL}/tenants/{tenant_id}", headers=headers)
    return redirect(url_for("tenants.listar"))