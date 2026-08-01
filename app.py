# app.py
from flask import Flask
from blueprints.auth import auth_bp
from blueprints.productos import productos_bp
from blueprints.impuestos import impuestos_bp
from blueprints.tenants import tenants_bp
from blueprints.usuarios import usuarios_bp
from blueprints.empresa import empresa_bp
from blueprints.clientes import clientes_bp
from blueprints.ventas import ventas_bp

app = Flask(__name__)
app.secret_key = "secret_frontend_key"

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(productos_bp)   # quedan bajo /productos
app.register_blueprint(impuestos_bp)   # /impuestos
app.register_blueprint(tenants_bp)     # /tenants
app.register_blueprint(usuarios_bp)    # /usuarios
app.register_blueprint(empresa_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(ventas_bp)


if __name__ == "__main__":
    app.run(port=5000, debug=True)