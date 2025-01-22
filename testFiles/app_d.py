from flask import Flask, render_template, request, jsonify
import searoute as sr

app = Flask(__name__)

# Definir os portos e suas coordenadas
ports = {
    "Santos": [-23.9608, -46.3336],
    "Rio de Janeiro": [-22.9035, -43.2096],
    "Barcelona": [41.3795, 2.1917],
    "Hamburgo": [53.5461, 9.9685]
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        port1 = request.form['port1']
        port2 = request.form['port2']

       

        origin_coords = ports[port1]
        destination_coords = ports[port2]

         # Fazer cópias das coordenadas para evitar modificar o original
        origin_coords = ports[port1][:]
        destination_coords = ports[port2][:]

        # Ajustar coordenadas para o formato esperado
        origin_coords[0], origin_coords[1] = origin_coords[1], origin_coords[0]
        destination_coords[0], destination_coords[1] = destination_coords[1], destination_coords[0]

        # Calcular a rota usando searoute
        route = sr.searoute(origin_coords, destination_coords, speed_knot=14, units="naut")

        coordinates = route['geometry']['coordinates']
        coordinates = [[coord[1], coord[0]] for coord in coordinates]  # Converter para [lat, lon]

        # Calcular a distância
        length_nautical = route.properties['length']
        length_km = length_nautical * 1.852

        # Retornar como JSON
        return jsonify({
            'coordinates': coordinates,
            'length_nautical': length_nautical,
            'length_km': length_km
        })

    return render_template('index_shippingintel.html', ports=ports)

if __name__ == "__main__":
    app.run(debug=True)
