from flask import Blueprint, request, jsonify
from models import Utente, db
from schemas import UtenteSchema
import hashlib
import uuid
from sqlalchemy import text
auth_bp = Blueprint('auth', __name__)
utente_schema = UtenteSchema()

# Funzione per generare userid come hash dello username

import uuid

# REGISTRAZIONE
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    role = data.get('role')
    tipologia_attore = data.get('tipologia_attore')
    companyname = data.get('companyname')  # nuovo campo opzionale
    geography = data.get('geography')      # nuovo campo opzionale

    if not username or not password or not confirm_password or not role:
        return jsonify({'error': 'Compila tutti i campi obbligatori'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Le password non coincidono'}), 400

    # stampa la query SQL per debug
    print(str(Utente.query.filter_by(username=username).statement.compile(compile_kwargs={"literal_binds": True})))

    if Utente.query.filter_by(username=username).first():
        return jsonify({'error': 'Username già esistente'}), 400

    new_user = Utente(
        username=username,
        password=password,  # Password salvata in chiaro (NON consigliato per produzione)
        role=role,
        tipologia_attore=tipologia_attore,
        companyname=companyname,
        geography=geography
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

    # DEBUG: stampa la query SQL completa con valore username
    print(str(Utente.query.filter(Utente.username == username).statement.compile(compile_kwargs={"literal_binds": True})))

    utente = Utente.query.filter(Utente.username == username).first()

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

@auth_bp.route('/user/profile', methods=['POST'])
def update_user_profile():
    data = request.get_json()

    userid = data.get("userid")
    if not userid:
        return jsonify({"error": "userid obbligatorio"}), 400

    utente = Utente.query.get(userid)
    if not utente:
        return jsonify({"error": "Utente non trovato"}), 404

    # Aggiorna solo i campi presenti nella richiesta
    if "companyname" in data:
        utente.companyname = data["companyname"]
    if "geography" in data:
        utente.geography = data["geography"]
    if "tipologia_attore" in data:
        utente.tipologia_attore = data["tipologia_attore"]

    db.session.commit()
    return jsonify({"message": "Profilo aggiornato con successo"}), 200

@auth_bp.route('/user/profile/<uuid:userid>', methods=['GET'])
def get_user_profile(userid):
    utente = Utente.query.get(userid)
    if not utente:
        return jsonify({"error": "Utente non trovato"}), 404

    return jsonify({
        "userid": str(utente.userid),
        "username": utente.username,
        "role": utente.role,
        "companyname": utente.companyname,
        "geography": utente.geography,
        "tipologia_attore": utente.tipologia_attore
    }), 200
