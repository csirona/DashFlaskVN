# blueprints/impuestos.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
from helpers import API_URL, login_required, get_headers

impuestos_bp = Blueprint("impuestos", __name__, url_prefix="/impuestos")

@impuestos_bp.route("/")
@login_required()
def listar():
    headers = get_headers()
    resp = requests.get(f"{API_URL}/impuestos/", headers=headers)
    impuestos = resp.json() if resp.status_code == 200 else []
    return render_template("impuestos.html", impuestos=impuestos)

@impuestos_bp.route("/crear", methods=["POST"])
@login_required()
def crear():
    headers = get_headers()
    data = {
        "descripcion": request.form["descripcion"],
        "codigo": int(request.form["codigo"]),  # ← AGREGAR CÓDIGO
        "tasa": float(request.form["tasa"])
    }
    
    resp = requests.post(f"{API_URL}/impuestos/", json=data, headers=headers)
    
    if resp.status_code != 201:
        error = resp.json().get("detail", "Error al crear impuesto")
        flash(error, "danger")
    else:
        flash("Impuesto creado exitosamente", "success")
    
    return redirect(url_for("impuestos.listar"))

@impuestos_bp.route("/editar/<int:impuesto_id>", methods=["POST"])
@login_required()
def editar(impuesto_id):
    headers = get_headers()
    data = {}
    
    if request.form.get("descripcion"):
        data["descripcion"] = request.form["descripcion"]
    if request.form.get("codigo"):
        data["codigo"] = int(request.form["codigo"])
    if request.form.get("tasa"):
        data["tasa"] = float(request.form["tasa"])
    
    resp = requests.put(f"{API_URL}/impuestos/{impuesto_id}", json=data, headers=headers)
    
    if resp.status_code != 200:
        error = resp.json().get("detail", "Error al editar impuesto")
        flash(error, "danger")
    else:
        flash("Impuesto actualizado exitosamente", "success")
    
    return redirect(url_for("impuestos.listar"))

@impuestos_bp.route("/eliminar/<int:impuesto_id>", methods=["POST"])
@login_required()
def eliminar(impuesto_id):
    headers = get_headers()
    resp = requests.delete(f"{API_URL}/impuestos/{impuesto_id}", headers=headers)
    
    if resp.status_code != 204:
        error = resp.json().get("detail", "Error al eliminar impuesto")
        flash(error, "danger")
    else:
        flash("Impuesto eliminado exitosamente", "success")
    
    return redirect(url_for("impuestos.listar"))