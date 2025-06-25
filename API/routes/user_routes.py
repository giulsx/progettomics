from flask import Blueprint, request, jsonify
from models import Utente, db
from schemas import UtenteSchema
import hashlib

auth_bp = Blueprint('auth', __name__)
utente_schema = UtenteSchema()

# Funzione per generare userid come hash dello username
def generate_userid(username):
    return hashlib.sha256(username.encode()).hexdigest()

# REGISTRAZIONE
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    role = data.get('role')
    companyname = data.get('companyname')
    geography = data.get('geography')
    tipologia_attore = data.get('tipologia_attore')

    if not username or not password or not confirm_password or not role:
        return jsonify({'error': 'Compila tutti i campi obbligatori'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Le password non coincidono'}), 400

    if Utente.query.filter_by(username=username).first():
        return jsonify({'error': 'Username già esistente'}), 400

    userid = generate_userid(username)

    new_user = Utente(
        userid=userid,
        username=username,
        password=password,  # Password salvata in chiaro (NON consigliato per produzione)
        role=role,
        companyname=companyname,
        geography=geography,
        tipologia_attore=tipologia_attore
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registrazione avvenuta con successo'}), 201


# POST: login e restituzione userid
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username e password obbligatori"}), 400

    utente = Utente.query.filter_by(username=username).first()

    if not utente:
        return jsonify({"message": "Utente non trovato"}), 404

    if utente.password != password:
        return jsonify({"message": "Password errata"}), 401

    return jsonify({
        "message": "Login effettuato con successo",
        "userid": str(utente.userid),
        "username": utente.username,
        "role": utente.role,
        "tipologia_attore": utente.tipologia_attore
    }), 200
