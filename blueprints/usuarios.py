# blueprints/usuarios.py
from flask import Blueprint, render_template, request, redirect, url_for
import requests
from helpers import API_URL, login_required, get_headers

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@usuarios_bp.route("/")
@login_required(role="admin")
def listar():
    headers = get_headers()
    resp = requests.get(f"{API_URL}/usuarios/", headers=headers)
    usuarios = resp.json() if resp.status_code == 200 else []
    return render_template("usuarios.html", usuarios=usuarios)

@usuarios_bp.route("/cambiar-password", methods=["POST"])
@login_required(role="admin")
def cambiar_password():
    headers = get_headers()
    user_id = request.form.get("user_id")
    new_password = request.form.get("new_password")
    requests.put(
        f"{API_URL}/usuarios/{user_id}/password",
        json={"new_password": new_password},
        headers=headers
    )
    return redirect(url_for("usuarios.listar"))