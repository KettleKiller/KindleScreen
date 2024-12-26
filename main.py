import os
import time
from PIL import Image, ImageChops
from PIL import ImageGrab
from flask import Flask, send_from_directory, render_template, jsonify
from flask_socketio import SocketIO, emit

# Parámetros
SAVE_DIR = "screenshots"
ASPECT_RATIO = (10, 9)  # Relación de aspecto 10:9
WIDTH = 1200  # Ancho de la imagen
OUTPUT_SIZE = (WIDTH * ASPECT_RATIO[0] // ASPECT_RATIO[1], WIDTH)  # Redimensionar según la relación de aspecto
FPS = 1  # Captura a 1 FPS
X_PARTS = 3  # Número de partes en X
Y_PARTS = 3  # Número de partes en Y

# Crear el directorio de captura si no existe
os.makedirs(SAVE_DIR, exist_ok=True)

# Nombre fijo para la imagen
IMAGE_NAME = "screenshot.png"

# Variable para almacenar la última imagen capturada
last_screenshot = None
last_parts = {}

# Crear la aplicación Flask
app = Flask(__name__)
socketio = SocketIO(app)

def capture_screenshots():
    global last_screenshot, last_parts

    while True:
        # Captura de pantalla
        screenshot = ImageGrab.grab()  # Captura de pantalla
        width, height = screenshot.size

        # Calcular dimensiones de recorte para mantener la relación de aspecto
        target_width = min(width, height * ASPECT_RATIO[0] // ASPECT_RATIO[1])
        target_height = min(height, width * ASPECT_RATIO[1] // ASPECT_RATIO[0])
        left = (width - target_width) // 2
        top = (height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        cropped = screenshot.crop((left, top, right, bottom))
        resized = cropped.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

        # Dividir la imagen en partes de X * Y
        part_width = OUTPUT_SIZE[0] // X_PARTS
        part_height = OUTPUT_SIZE[1] // Y_PARTS

        # Comparar y actualizar las partes si es necesario
        for i in range(Y_PARTS):
            for j in range(X_PARTS):
                # Definir la caja de la sub-imagen
                left = j * part_width
                top = i * part_height
                right = left + part_width
                bottom = top + part_height

                part = resized.crop((left, top, right, bottom))

                # Generar un identificador único para cada parte
                part_id = i * X_PARTS + j + 1

                # Comparar la sub-imagen con la anterior
                if part_id not in last_parts or ImageChops.difference(part, last_parts[part_id]).getbbox():
                    # Si es la primera captura o hay diferencias, actualizar la imagen
                    part_filepath = os.path.join(SAVE_DIR, f"{part_id}.png")
                    part.save(part_filepath)
                    last_parts[part_id] = part
                    
                    # Enviar una notificación al cliente sobre la actualización
                    socketio.emit('image_updated', {'part_id': part_id})

        time.sleep(1 / FPS)  # Esperar para mantener la tasa de FPS

# Ruta de inicio para la página
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/screenshots/<filename>")
def serve_screenshot(filename):
    # Verificar si el archivo existe
    filepath = os.path.join(SAVE_DIR, filename)
    if os.path.exists(filepath):
        return send_from_directory(SAVE_DIR, filename)
    return "Archivo no encontrado", 404

@app.route("/screenshots")
def list_screenshots():
    # Generar lista de imágenes en formato JSON
    screenshot_list = [{"id": i, "src": f"/screenshots/{i}.png"} for i in range(1, X_PARTS * Y_PARTS + 1)]
    return jsonify(screenshot_list)

if __name__ == "__main__":
    from threading import Thread

    # Iniciar el hilo de captura de pantallas
    screenshot_thread = Thread(target=capture_screenshots, daemon=True)
    screenshot_thread.start()

    # Iniciar el servidor Flask con WebSocket
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
