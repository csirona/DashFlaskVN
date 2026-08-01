# blueprints/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
from jose import jwt
from helpers import API_URL, is_logged, has_role

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if is_logged():
        return redirect(url_for("auth.redirect_by_role"))

    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        resp = requests.post(f"{API_URL}/login", data={"username": username, "password": password})

        if resp.status_code == 200:
            token = resp.json()["access_token"]
            payload = jwt.get_unverified_claims(token)
            session["token"] = token
            session["role"] = payload.get("role")
            session["username"] = username
            session["tenant_id"] = payload.get("tenant_id")
            return redirect(url_for("auth.redirect_by_role"))
        else:
            error = "Credenciales incorrectas"

    return render_template("login.html", error=error)

# blueprints/auth.py (fragmento corregido)

@auth_bp.route("/redirect-by-role")
def redirect_by_role():
    if not is_logged():
        return redirect(url_for("auth.login"))
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("usuarios.listar"))   # antes ponía "usuarios.admin_usuarios"
    elif role == "cliente":
        return redirect(url_for("productos.listar"))  # o la ruta que desees para clientes
    return redirect(url_for("auth.home"))

@auth_bp.route("/home")
def home():
    # ... (puedes mover el código anterior aquí)
    pass

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))