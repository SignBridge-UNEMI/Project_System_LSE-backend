import os
import pandas as pd
from mediapipe.python.solutions.holistic import Holistic
from helpers import create_folder, get_keypoints, insert_keypoints_sequence
from constants import KEYPOINTS_PATH, ROOT_PATH, FRAME_ACTIONS_PATH

def create_keypoints(word_id: str, words_path: str, hdf_path: str) -> None:
    """
    ### CREAR KEYPOINTS PARA UNA PALABRA
    Recorre la carpeta de frames de la palabra y guarda sus keypoints en `hdf_path`.

    :param word_id: Identificador de la palabra para la que se crearán los keypoints.
    :param words_path: Ruta a la carpeta donde están almacenadas las muestras de la palabra.
    :param hdf_path: Ruta del archivo HDF donde se guardarán los keypoints.
    """
    data = pd.DataFrame([])
    frames_path = os.path.join(words_path, word_id)

    # Verifica si la carpeta de frames existe
    if not os.path.exists(frames_path):
        print(f"Error: La carpeta para la palabra '{word_id}' no existe en {frames_path}.")
        return

    with Holistic() as holistic:
        print(f'Creando keypoints de "{word_id}"...')
        sample_list = os.listdir(frames_path)
        sample_count = len(sample_list)

        for n_sample, sample_name in enumerate(sample_list, start=1):
            sample_path = os.path.join(frames_path, sample_name)
            keypoints_sequence = get_keypoints(holistic, sample_path)
            data = insert_keypoints_sequence(data, n_sample, keypoints_sequence)
            print(f"{n_sample}/{sample_count}", end="\r")

    # Guarda los keypoints en el archivo HDF
    data.to_hdf(hdf_path, key="data", mode="w")
    print(f"\nKeypoints creados! ({sample_count} muestras)")

if __name__ == "__main__":
    # Crea la carpeta `keypoints` si no existe
    create_folder(KEYPOINTS_PATH)

    # GENERAR TODAS LAS PALABRAS
    word_ids = [word for word in os.listdir(os.path.join(ROOT_PATH, FRAME_ACTIONS_PATH))]

    # Generar para una palabra o conjunto específico
    # word_ids = ["bien"]
    # word_ids = ["buenos_dias", "como_estas", "disculpa", "gracias", "hola-der", "hola-izq", "mal", "mas_o_menos", "me_ayudas", "por_favor"]

    for word_id in word_ids:
        hdf_path = os.path.join(KEYPOINTS_PATH, f"{word_id}.h5")
        create_keypoints(word_id, FRAME_ACTIONS_PATH, hdf_path)
