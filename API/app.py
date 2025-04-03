from flask import Flask
from config import DATABASE_URL
from database import db
from schemas import ma
from routes import app_routes

app = Flask(__name__)

# Configurazione del database
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inizializzazione delle estensioni
db.init_app(app)
ma.init_app(app)

# Registrazione delle route
app.register_blueprint(app_routes)

# Creazione delle tabelle al primo avvio
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
