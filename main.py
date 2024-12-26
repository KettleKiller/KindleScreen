import os
import time
from PIL import Image, ImageChops, ImageDraw
from PIL import ImageGrab
import pyautogui
from flask import Flask, send_from_directory, render_template, jsonify

# Parámetros
SAVE_DIR = "lastState"
ASPECT_RATIO = (10, 9)  # Relación de aspecto 10:9
WIDTH = 1200  # Ancho de la imagen
OUTPUT_SIZE = (WIDTH * ASPECT_RATIO[0] // ASPECT_RATIO[1], WIDTH)  # Redimensionar según la relación de aspecto
FPS = 1  # Captura a 1 FPS

# Crear el directorio de captura si no existe
os.makedirs(SAVE_DIR, exist_ok=True)

# Nombre fijo para la imagen
IMAGE_NAME = "State.png"

# Variable para almacenar la última imagen capturada
last_screenshot = None

def capture_screenshots():
    global last_screenshot

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

        # Obtener la posición del ratón
        mouse_x, mouse_y = pyautogui.position()

        # Calcular las coordenadas escaladas para la imagen redimensionada
        scale_x = OUTPUT_SIZE[0] / width
        scale_y = OUTPUT_SIZE[1] / height
        scaled_mouse_x = int(mouse_x * scale_x)
        scaled_mouse_y = int(mouse_y * scale_y)

        # Dibujar el cursor en la imagen redimensionada
        draw = ImageDraw.Draw(resized)
        cursor_radius = 10  # Tamaño del cursor
        cursor_color = (255, 0, 0)  # Color rojo
        draw.ellipse((scaled_mouse_x - cursor_radius, scaled_mouse_y - cursor_radius,
                      scaled_mouse_x + cursor_radius, scaled_mouse_y + cursor_radius), fill=cursor_color)

        # Si es la primera captura, guarda la imagen sin comparación
        if last_screenshot is None:
            last_screenshot = resized
            new_filepath = os.path.join(SAVE_DIR, IMAGE_NAME)
            resized.save(new_filepath)
            print("Primera captura guardada.")
        
        else:
            # Comparar la nueva imagen con la anterior
            diff = ImageChops.difference(resized, last_screenshot)
            if diff.getbbox() is not None:  # Si hay diferencias
                # Si hay diferencias, guardar la nueva imagen
                last_screenshot = resized
                new_filepath = os.path.join(SAVE_DIR, IMAGE_NAME)
                resized.save(new_filepath)
                print("Imagen actualizada.")
            else:
                # Si no hay diferencias, no guardes la imagen y espera un ciclo.
                print("No hay cambios en la pantalla, no se guarda nueva imagen.")

        time.sleep(1 / FPS)  # Esperar para mantener la tasa de FPS

# Crear la aplicación Flask
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/screenshots/<filename>")
def serve_screenshot(filename):
    # Verificar si el archivo existe
    if filename == IMAGE_NAME:
        return send_from_directory(SAVE_DIR, filename)
    return "Archivo no encontrado", 404

@app.route("/screenshots")
def list_screenshots():
    # Solo se necesita devolver el nombre de la imagen fija
    return jsonify({"new_image": IMAGE_NAME})

if __name__ == "__main__":
    from threading import Thread

    # Iniciar el hilo de captura de pantallas
    screenshot_thread = Thread(target=capture_screenshots, daemon=True)
    screenshot_thread.start()

    # Iniciar el servidor Flask
    app.run(debug=True, host="0.0.0.0", port=5000)
