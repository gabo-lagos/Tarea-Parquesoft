from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt
)
from datetime import timedelta
import sys

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-change-me'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

users = {
    'alice': {'password': generate_password_hash('alicepass'), 'role': 'client'},
    'bob': {'password': generate_password_hash('bobpass'), 'role': 'manager'},
    'carol': {'password': generate_password_hash('carolpass'), 'role': 'admin'}
}

juguetes = [
    {
        "id": 1,
        "nombre": "Porsche 917LH",
        "categoria": "Carros",
        "edad_recomendada": "3+",
        "precio": 10000.0,
        "marca": "Hot Wheels"
    },
    {
        "id": 2,
        "nombre": "Aston Martin DB4GT",
        "categoria": "Carros",
        "edad_recomendada": "3+",
        "precio": 10000.0,
        "marca": "Hot Wheels"
    },
    {
        "id": 3,
        "nombre": "Hot Wheels NIGHTBURNERZ",
        "categoria": "Paquetes de carros",
        "edad_recomendada": "3+",
        "precio": 54900.0,
        "marca": "Hot Wheels"
    },
    {
        "id": 4,
        "nombre": "Monoplaza Ferrari F1",
        "categoria": "Carros a escala",
        "edad_recomendada": "6+",
        "precio": 20000.0,
        "marca": "LEGO"
    },
    {
        "id": 5,
        "nombre": "Pelota de futbol",
        "categoria": "Deportes",
        "edad_recomendada": "7+",
        "precio": 160000.0,
        "marca": "Adidas"
    }
]

def role_required(allowed_roles):
    def wrapper(fn):
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            role = claims.get('role')
            if role not in allowed_roles:
                return jsonify({"msg": "El usuario no tiene el rol requerido"}), 403
            return fn(*args, **kwargs)
        decorator.__name__ = fn.__name__
        return decorator
    return wrapper

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "mensaje": "✅ API Flask JWT en ejecución",
        "endpoints": {
            "POST /login": "Obtener token JWT",
            "GET /juguetes": "Público - lista de juguetes",
            "POST /juguetes": "Autenticado - agregar juguete",
            "DELETE /juguetes/<id>": "Manager/Admin - eliminar juguete",
            "GET /reports": "Manager/Admin - reportes",
            "POST /users": "Admin - crear nuevo usuario"
        }
    }), 200

@app.route('/juguetes', methods=['GET'])
def get_all_juguetes():
    
    categoria = request.args.get('categoria')
    marca = request.args.get('marca')

    resultados = juguetes
    if categoria:
        resultados = [j for j in resultados if j["categoria"].lower() == categoria.lower()]
    if marca:
        resultados = [j for j in resultados if j["marca"].lower() == marca.lower()]

    return jsonify(resultados)

@app.route('/juguetes', methods=['POST'])
@jwt_required()
def add_juguete():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Falta el cuerpo JSON"}), 400
    data["id"] = (juguetes[-1]['id'] + 1) if juguetes else 1
    juguetes.append(data)
    return jsonify(data), 201

@app.route('/juguetes/<int:id>', methods=['DELETE'])
@role_required(['manager', 'admin'])
def delete_juguete(id):
    global juguetes
    encontrado = [j for j in juguetes if j['id'] == id]
    if not encontrado:
        return jsonify({"error": "Juguete no encontrado"}), 404
    juguetes = [j for j in juguetes if j['id'] != id]
    return jsonify({"mensaje": f"Juguete con ID {id} eliminado"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "Falta nombre de usuario o contraseña"}), 400

    username = data['username']
    password = data['password']
    user = users.get(username)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401

    claims = {"role": user['role']}
    token = create_access_token(identity=username, additional_claims=claims)
    return jsonify(access_token=token, role=user['role']), 200

@app.route('/usuarios', methods=['POST'])
@role_required(['admin'])
def add_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data or 'role' not in data:
        return jsonify({"msg": "Se requiere username, password y role"}), 400

    username = data['username']
    if username in users:
        return jsonify({"msg": "El usuario ya existe"}), 409

    role = data['role']
    if role not in ['client', 'manager', 'admin']:
        return jsonify({"msg": "Rol inválido"}), 400

    users[username] = {
        'password': generate_password_hash(data['password']),
        'role': role
    }
    return jsonify({"msg": "Usuario creado", "username": username, "role": role}), 201

@app.route('/reports', methods=['GET'])
@role_required(['manager', 'admin'])
def reports():
    return jsonify({"msg": "Datos de reporte confidenciales"}), 200

@jwt.unauthorized_loader
def custom_unauthorized_response(callback):
    return jsonify({"msg": "Falta el encabezado de autorización"}), 401

@jwt.invalid_token_loader
def custom_invalid_token(reason):
    return jsonify({"msg": "Token inválido"}), 422

def run_basic_tests():
    print("Ejecutando pruebas básicas...")
    client = app.test_client()

    rv = client.post('/login', json={'username': 'carol', 'password': 'carolpass'})
    print('/login (carol) estado:', rv.status_code, 'respuesta:', rv.get_json())
    assert rv.status_code == 200
    token = rv.get_json().get('access_token')

    rv = client.post('/login', json={'username': 'carol', 'password': 'wrong'})
    print('/login contraseña incorrecta estado:', rv.status_code, 'respuesta:', rv.get_json())
    assert rv.status_code == 401

    rv = client.post('/juguetes', json={'nombre': 'X'})
    print('/juguetes sin token estado:', rv.status_code, 'respuesta:', rv.get_json())
    assert rv.status_code == 401

    rv = client.get('/reports', headers={'Authorization': 'Bearer invalid.token'})
    print('/reports token inválido estado:', rv.status_code, 'respuesta:', rv.get_json())
    assert rv.status_code == 422

    rv = client.post('/login', json={'username': 'alice', 'password': 'alicepass'})
    alice_token = rv.get_json().get('access_token')
    rv = client.delete('/juguetes/1', headers={'Authorization': f'Bearer {alice_token}'})
    print('/juguetes eliminar como alice estado:', rv.status_code, 'respuesta:', rv.get_json())
    assert rv.status_code == 403


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        run_basic_tests()
    else:
        app.run(host='0.0.0.0',
                 port=8003, 
                 debug=False, 
                 use_reloader=False
            )
