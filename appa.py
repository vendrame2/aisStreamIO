from flask import Flask, render_template, Response
import asyncio
import websockets
import json
from datetime import datetime, timezone
from threading import Thread

app = Flask(__name__)

# Variável global para armazenar mensagens recebidas
ais_messages = []

# Configuração do WebSocket
API_KEY = ""  # Insira sua chave de API
WEBSOCKET_URL = "wss://stream.aisstream.io/v0/stream"
SUBSCRIBE_MESSAGE = {
    "APIKey": API_KEY,
    "BoundingBoxes": [[[-11, -178], [30, 74]]],
    "FiltersShipMMSI": ["538007480", "636015988", "316003701"],
    "FilterMessageTypes": ["PositionReport"],
}

# Função para conectar ao WebSocket e armazenar mensagens
async def connect_ais_stream():
    global ais_messages
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        # Enviar mensagem de inscrição
        await websocket.send(json.dumps(SUBSCRIBE_MESSAGE))

        # Receber mensagens do WebSocket
        async for message_json in websocket:
            message = json.loads(message_json)
            if "Message" in message and "PositionReport" in message["Message"]:
                ais_message = message["Message"]["PositionReport"]
                formatted_message = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "ship_id": ais_message["UserID"],
                    "latitude": ais_message["Latitude"],
                    "longitude": ais_message["Longitude"],
                }
                ais_messages.append(formatted_message)

# Iniciar a conexão WebSocket em uma thread separada
def start_websocket_thread():
    asyncio.run(connect_ais_stream())

thread = Thread(target=start_websocket_thread)
thread.daemon = True
thread.start()

# Rota para exibir mensagens recebidas
@app.route("/")
def index():
    return render_template("index.html")

# Rota para enviar mensagens em tempo real
@app.route("/stream")
def stream():
    def message_generator():
        last_index = 0
        while True:
            if len(ais_messages) > last_index:
                for msg in ais_messages[last_index:]:
                    yield f"data: {json.dumps(msg)}\n\n"
                last_index = len(ais_messages)
            asyncio.sleep(1)
    return Response(message_generator(), content_type="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)