from flask import Flask, render_template, request, jsonify
import searoute as sr

app = Flask(__name__)

# Definir os portos e suas coordenadas (substitua com portos reais conforme necessário)
ports = {
    "Porto de Santos": [-23.99049, -46.30390],
    "Porto de Rio de Janeiro": [-22.892850, -43.188211],
    "Porto de Barcelona": [41.3506189485991, 2.1669922169211606],
    "Porto de Hamburgo": [53.54049, 9.98820], 
    "Itajai, SC": [-26.9083, -48.6626]
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']

        # Fazer cópias das coordenadas para evitar modificar os valores originais no dicionário
        origin_coords = ports[origin][:]
        destination_coords = ports[destination][:]

        #Typically latitude precedes longitude when expressing coordinates (Bowditch, 2019; GISGeography, 2023) however Searoute inexplicably swaps the values. Therefore, the coordinate elements must be swapped.
        origin_coords[0], origin_coords[1] = origin_coords[1], origin_coords[0]
        print(origin_coords[0], origin_coords[1])
        destination_coords[0], destination_coords[1] = destination_coords[1], destination_coords[0]
        print(destination_coords[0], destination_coords[1])
        # Calcular a rota usando searoute
        route = sr.searoute(origin_coords, destination_coords, speed_knot=14, units="naut")

        coordinates = route['geometry']['coordinates']
        print(coordinates)
        coordinates = [[coord[1], coord[0]] for coord in coordinates]  # Revertendo a ordem para [lat, lon]

        # Calcular a distância em milhas náuticas e quilômetros
        length_nautical = route.properties['length']
        length_km = length_nautical * 1.852  # Conversão de milhas náuticas para quilômetros

        duration_hours = route.properties['duration_hours']

        # Retornar os dados da rota e as distâncias em formato JSON
        return jsonify({
            'coordinates': coordinates,
            'length_nautical': length_nautical,
            'length_km': length_km,
            'duration_hours':duration_hours
        })

    return render_template('index2.html', ports=ports)

if __name__ == "__main__":
    app.run(debug=True)