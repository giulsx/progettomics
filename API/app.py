from flask import Flask
from config import DATABASE_URL
from database import db
from schemas import ma
from flask_cors import CORS 
# from routes import app_routes
from routes.product_routes import product_bp
from routes.activity_routes import activity_bp
from routes.user_routes import auth_bp
from routes.certificazioni_routes import certificazioni_bp

 
app = Flask(__name__)
CORS(app)  

# Configurazione del database
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inizializzazione delle estensioni
db.init_app(app)
ma.init_app(app)

# Registrazione delle route
# app.register_blueprint(app_routes)
app.register_blueprint(product_bp)
app.register_blueprint(activity_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(certificazioni_bp)


@app.route("/ping", methods=["GET"])
def ping():
    return {"message": "pong"}, 200


# Creazione delle tabelle al primo avvio
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=8000)