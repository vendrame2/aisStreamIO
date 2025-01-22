from flask import Flask, render_template, request, jsonify
import searoute as sr
import requests

app = Flask(__name__)

# Definir os portos e suas coordenadas
ports = {
    "Saints": [-23.99049, -46.30390],
    "Rio de Janeiro": [-22.892850, -43.188211],
    "Barcelona": [41.3506189485991, 2.1669922169211606],
    "Hamburgo": [53.54049, 9.98820], 
    "Itajai": [-26.9083, -48.6626],
    "Rotterdam":[51.94978261106388, 4.145273726520706],
    "Shanghai":[30.626995034755673, 122.06350187894172],
    "Busan": [35.104417043279796, 129.0423876468511]
}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']

        # Fazer cópias das coordenadas para evitar modificar os valores originais no dicionário
        origin_coords = ports[origin][:]
        destination_coords = ports[destination][:]

        # Ajustar as coordenadas para o formato esperado pela biblioteca searoute
        origin_coords[0], origin_coords[1] = origin_coords[1], origin_coords[0]
        destination_coords[0], destination_coords[1] = destination_coords[1], destination_coords[0]

        # Calcular a rota usando searoute
        route = sr.searoute(origin_coords, destination_coords, speed_knot=14, units="naut")

        coordinates = route['geometry']['coordinates']
        coordinates = [[coord[1], coord[0]] for coord in coordinates]  # Reverter ordem para [lat, lon]

        length_nautical = route.properties['length']
        length_km = length_nautical * 1.852  # Conversão de milhas náuticas para quilômetros
        duration_hours = route.properties['duration_hours']

        return jsonify({
            'coordinates': coordinates,
            'length_nautical': length_nautical,
            'length_km': length_km,
            'duration_hours': duration_hours
        })

    return render_template('indexU.html', ports=ports)


@app.route('/api', methods=['POST'])
def api_route():
    try:
        # Obtendo os parâmetros enviados para a API
        port1 = request.form.get("port1")
        port2 = request.form.get("port2")

        if not port1 or not port2:
            return jsonify({"error": "Both port1 and port2 are required"}), 400

        # URLs das APIs externas
        distance_url = "https://www.shippingintel.com/api/calculate_distance"
        route_url = "https://www.shippingintel.com/api/calculate_route"

        # Chamadas simultâneas para as APIs externas
        distance_response = requests.post(distance_url, data={"port1": port1, "port2": port2})
        
        route_response = requests.post(route_url, data={"port1": port1, "port2": port2})
        

        # Verificando respostas das APIs
        
        # if distance_response.status_code != 200:
        #     return jsonify({
        #         "error": "Error calculating distance",
        #         "details": distance_response.text
        #     }), 500
        
        # if route_response.status_code != 200:
        #     return jsonify({
        #         "error": "Error calculating route",
        #         "details": route_response.text
        #     }), 500

        # Extraindo dados das respostas
        distance_data = distance_response.json()
        route_data = route_response.json()
        #print(route_data)
        # Construindo a resposta consolidada
        response = {
            "distance": distance_data,
            "route": route_data,
            "map_data": {
                "distance_route": f"Generated map for distance between {port1} and {port2}",
                "route_path": f"Generated path for route between {port1} and {port2}"
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
