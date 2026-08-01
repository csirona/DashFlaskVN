# helpers.py
from flask import session, redirect, url_for

API_URL = "http://127.0.0.1:8000"

def is_logged():
    return "token" in session

def has_role(role):
    return session.get("role") == role

def login_required(role=None):
    """Decorador para rutas que requieren autenticación y opcionalmente un rol."""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_logged():
                return redirect(url_for("auth.login"))
            if role and not has_role(role):
                return redirect(url_for("auth.redirect_by_role"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_headers():
    """Devuelve las cabeceras con el token JWT actual."""
    token = session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}