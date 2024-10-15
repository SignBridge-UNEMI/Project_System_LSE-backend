"""
constants.py

Este módulo contiene configuraciones y constantes utilizadas en el proyecto.
"""

import os
import cv2

# SETTINGS
MIN_LENGTH_FRAMES = 5  # Número mínimo de frames
LENGTH_KEYPOINTS = 1662  # Longitud de los puntos clave
MODEL_FRAMES = 15  # Número de frames para el modelo

# PATHS
ROOT_PATH = os.getcwd()  # Ruta raíz del proyecto
FRAME_ACTIONS_PATH = os.path.join(ROOT_PATH, "frame_actions")  # Ruta para las acciones de frames
DATA_PATH = os.path.join(ROOT_PATH, "data")  # Ruta para los datos
DATA_JSON_PATH = os.path.join(DATA_PATH, "data.json")  # Ruta para el archivo JSON de datos
MODEL_FOLDER_PATH = os.path.join(ROOT_PATH, "models")  # Ruta para los modelos
MODEL_PATH = os.path.join(MODEL_FOLDER_PATH, f"actions_{MODEL_FRAMES}.keras")  # Ruta para el modelo específico
KEYPOINTS_PATH = os.path.join(DATA_PATH, "keypoints")  # Ruta para los puntos clave
WORDS_JSON_PATH = os.path.join(MODEL_FOLDER_PATH, "words.json")  # Ruta para el archivo JSON de palabras

# SHOW IMAGE PARAMETERS
FONT = cv2.FONT_HERSHEY_PLAIN  # Tipo de fuente para mostrar imágenes
FONT_SIZE = 1.5  # Tamaño de la fuente
FONT_POS = (5, 30)  # Posición de la fuente en la imagen

# Diccionario de palabras y sus traducciones
words_text = {
    "adios": "ADIÓS",
    "bien": "BIEN",
    "buenas_noches": "BUENAS NOCHES",
    "buenas_tardes": "BUENAS TARDES",
    "buenos_dias": "BUENOS DÍAS",
    "como_estas": "COMO ESTÁS",
    "disculpa": "DISCULPA",
    "gracias": "GRACIAS",
    "hola": "HOLA",
    "mal": "MAL",
    "mas_o_menos": "MAS O MENOS",
    "me_ayudas": "ME AYUDAS",
    "por_favor": "POR FAVOR",
}
