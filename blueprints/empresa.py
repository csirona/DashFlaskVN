from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
from helpers import API_URL, login_required, get_headers

empresa_bp = Blueprint("empresa", __name__, url_prefix="/empresa")

@empresa_bp.route("/")
@login_required()
def mi_empresa():
    headers = get_headers()
    resp = requests.get(f"{API_URL}/mi-empresa", headers=headers)
    if resp.status_code == 200:
        empresa = resp.json()
    else:
        empresa = None
    return render_template("mi_empresa.html", empresa=empresa, username=session.get("username"))

@empresa_bp.route("/actualizar", methods=["POST"])
@login_required()
def actualizar():
    headers = get_headers()
    data = {
        "razon_social": request.form.get("razon_social"),
        "rut": request.form.get("rut"),
        "dv": request.form.get("dv"),
        "giro": request.form.get("giro"),
        "direccion": request.form.get("direccion"),
        "telefono": request.form.get("telefono"),
        "email": request.form.get("email"),
        "ciudad": request.form.get("ciudad"),       # <-- añadir
        "comuna": request.form.get("comuna"), 
    }
    requests.put(f"{API_URL}/mi-empresa", json=data, headers=headers)
    return redirect(url_for("empresa.mi_empresa"))