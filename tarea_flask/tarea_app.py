from flask import Flask, jsonify, request

app = Flask(__name__)

juguetes = [
    {
        "id": 1,
        "nombre": "Porsche 917LH",
        "categoria": "Carros",
        "edad_recomendada": "3+",
        "precio": 10.000,
        "marca": "Hot Wheels"
    },
    {
        "id": 2,
        "nombre": "Aston Martin DB4GT",
        "categoria": "Carros",
        "edad_recomendada": "3+",
        "precio": 10.000, 
        "marca": "Hot Wheels"
    },
    {
        "id": 3,
        "nombre": "Hot Wheels NIGHTBURNERZ",
        "categoria": "Paquetes de carros",
        "edad_recomendada": "3+",
        "precio": 54.900,
        "marca": "Hot Wheels"
    },
    {
        "id": 4,
        "nombre": "Monoplaza Ferrari F1",
        "categoria": "Carros a escala",
        "edad_recomendada": "6+",
        "precio": 20.000,
        "marca": "LEGO"
    },
    {
        "id": 5,
        "nombre": "Pelota de futbol",
        "categoria": "Deportes",
        "edad_recomendada": "7+",
        "precio": 160.000,
        "marca": "Adidas"
    }
]


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

@app.route('/juguetes/<id>', methods=['GET'])
def get_juguete(id):
    juguete = list(filter(lambda j: j["id"] == int(id), juguetes))
    if juguete:
        return jsonify(juguete[0])
    else:
        return jsonify({"error": "Juguete no encontrado"}), 404

@app.route('/juguetes', methods=['POST'])
def add_juguete():
    data = request.get_json()
    data["id"] = len(juguetes) + 1
    juguetes.append(data)
    return jsonify(data), 201

@app.route('/juguetes/<int:id>', methods=['DELETE'])
def delete_juguete(id ):
    global juguetes
    if juguetes:
        juguetes = list(filter(lambda j: j["id"] != int(id), juguetes))
        return  jsonify({"mensaje": f"Juguete con ID {id} eliminado"}), 200
    else:
        return jsonify({"error": "Juguete no encontrado"}), 404

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 8003,
        debug = True
    )