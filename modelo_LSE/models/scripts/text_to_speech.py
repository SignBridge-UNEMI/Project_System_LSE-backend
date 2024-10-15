from gtts import gTTS
import os
import pygame
from time import sleep

def text_to_speech(text):
    """
    Convierte el texto proporcionado en audio y lo reproduce.
    
    Parámetros:
    - text (str): El texto que se va a convertir a habla.
    
    El audio generado se guarda como un archivo temporal 'speech.mp3', que se
    reproduce utilizando la biblioteca pygame. Después de la reproducción, 
    el archivo se elimina para liberar espacio.
    """
    # Crear el objeto gTTS para convertir el texto a habla
    tts = gTTS(text=text, lang='es')
    filename = "speech.mp3"  # Nombre del archivo de audio a guardar
    tts.save(filename)  # Guardar el archivo de audio

    # Inicializar pygame para la reproducción de audio
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(filename)  # Cargar el archivo de audio
    pygame.mixer.music.play()  # Reproducir el audio
    
    # Esperar hasta que el audio termine de reproducirse
    while pygame.mixer.music.get_busy():
        sleep(1)  # Esperar 1 segundo

    # Limpiar el mezclador y cerrar pygame
    pygame.mixer.quit()
    pygame.quit()

    # Eliminar el archivo de audio después de la reproducción
    os.remove(filename)

if __name__ == "__main__":
    # Bloque de prueba para verificar la funcionalidad del módulo
    text = "texto"  # Texto de prueba
    text_to_speech(text)  # Llamar a la función con el texto de prueba
