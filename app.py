

from flask import Flask, Response, render_template
import asyncio
import websockets
import json
from dotenv import load_dotenv
import os
app = Flask(__name__)

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Dados de navios em memória
navios = []

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/stream')
def stream():
    def generate():
        while True:
            if navios:
                for navio in navios:
                    yield f"data: {json.dumps(navio)}\n\n"
            asyncio.sleep(1)  # Evitar sobrecarregar o cliente
    return Response(generate(), content_type='text/event-stream')

async def connect_ais_stream():
    global navios
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        if not API_KEY:
            raise ValueError("API_KEY não está definida. Verifique o arquivo .env.")
        
        subscribe_message = {"APIKey": API_KEY, 
                             "BoundingBoxes": [
                                 [[-22.9068, -48.6619], [-26.9020, -43.1729]], #Santos
                                # [[42.15, -9.5], [36.95, -6.0]],         # Portugal Continental
                                # [[39.73, -31.27], [36.85, -24.75]],     # Açores
                                # [[33.50, -17.40], [32.30, -16.25]],     # Madeira
                                # [[43.80, -9.30], [36.00, 3.30]],        # Espanha Continental
                                # [[40.10, 1.10], [38.60, 4.50]],         # Ilhas Baleares
                                # [[29.25, -18.20], [27.65, -13.30]]      # Ilhas Canárias
                                 ]}
        await websocket.send(json.dumps(subscribe_message))
        async for message_json in websocket:
            message = json.loads(message_json)
            if message["MessageType"] == "PositionReport":
                ais_message = message['Message']['PositionReport']
                navio = {
                    "ShipId": ais_message['UserID'],
                    "Latitude": ais_message['Latitude'],
                    "Longitude": ais_message['Longitude']
                }
                navios.append(navio)  # Adiciona ou atualiza o navio
                if len(navios) > 3000:
                    navios.pop(0)  # Limita a quantidade de navios em memória

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(connect_ais_stream())
    app.run(debug=True, threaded=True)