import json
import os
import cv2
import numpy as np
import pandas as pd
from typing import NamedTuple, List
from mediapipe.python.solutions.holistic import (
    FACEMESH_CONTOURS, 
    POSE_CONNECTIONS, 
    HAND_CONNECTIONS
)
from mediapipe.python.solutions.drawing_utils import draw_landmarks, DrawingSpec
from constants import *

# GENERAL
def mediapipe_detection(image: np.ndarray, model) -> NamedTuple:
    """
    Realiza la detección mediapipe en una imagen.

    :param image: Imagen en la que se realizará la detección.
    :param model: Modelo mediapipe utilizado para la detección.
    :return: Resultados de la detección.
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    return results

def create_folder(path: str) -> None:
    """
    Crea una carpeta si no existe.

    :param path: Ruta de la carpeta a crear.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def there_hand(results: NamedTuple) -> bool:
    """
    Verifica si hay manos detectadas en los resultados.

    :param results: Resultados de la detección mediapipe.
    :return: True si hay manos detectadas, False en caso contrario.
    """
    return results.left_hand_landmarks or results.right_hand_landmarks

def get_word_ids(path: str) -> List[str]:
    """
    Obtiene los IDs de las palabras desde un archivo JSON.

    :param path: Ruta del archivo JSON.
    :return: Lista de IDs de palabras.
    """
    with open(path, 'r') as json_file:
        data = json.load(json_file)
        return data.get('word_ids', [])

# CAPTURE SAMPLES
def draw_keypoints(image: np.ndarray, results: NamedTuple) -> None:
    """
    Dibuja los keypoints en la imagen utilizando los resultados de mediapipe.

    :param image: Imagen donde se dibujarán los keypoints.
    :param results: Resultados de la detección de mediapipe.
    """
    if results.face_landmarks:
        draw_landmarks(
            image,
            results.face_landmarks,
            FACEMESH_CONTOURS,
            DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
            DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1),
        )
    if results.pose_landmarks:
        draw_landmarks(
            image,
            results.pose_landmarks,
            POSE_CONNECTIONS,
            DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
            DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2),
        )
    if results.left_hand_landmarks:
        draw_landmarks(
            image,
            results.left_hand_landmarks,
            HAND_CONNECTIONS,
            DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
            DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2),
        )
    if results.right_hand_landmarks:
        draw_landmarks(
            image,
            results.right_hand_landmarks,
            HAND_CONNECTIONS,
            DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
            DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2),
        )

def save_frames(frames: List[np.ndarray], output_folder: str) -> None:
    """
    Guarda los frames en la carpeta de salida especificada.

    :param frames: Lista de frames a guardar.
    :param output_folder: Ruta de la carpeta de salida.
    """
    for num_frame, frame in enumerate(frames):
        frame_path = os.path.join(output_folder, f"{num_frame + 1}.jpg")
        cv2.imwrite(frame_path, cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA))

# CREATE KEYPOINTS
def extract_keypoints(results: NamedTuple) -> np.ndarray:
    """
    Extrae los keypoints de los resultados de detección.

    :param results: Resultados de la detección mediapipe.
    :return: Un array de keypoints extraídos.
    """
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, face, lh, rh])

def get_keypoints(model, sample_path: str) -> np.ndarray:
    """
    Obtiene los keypoints de una muestra de imágenes.

    :param model: Modelo mediapipe utilizado para la detección.
    :param sample_path: Ruta de la carpeta que contiene las imágenes de la muestra.
    :return: Una secuencia de keypoints de la muestra.
    """
    kp_seq = np.array([])
    try:
        for img_name in os.listdir(sample_path):
            img_path = os.path.join(sample_path, img_name)
            frame = cv2.imread(img_path)
            if frame is None:
                print(f"Error leyendo la imagen {img_path}")
                continue
            results = mediapipe_detection(frame, model)
            kp_frame = extract_keypoints(results)
            kp_seq = np.concatenate([kp_seq, [kp_frame]] if kp_seq.size > 0 else [[kp_frame]])
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    return kp_seq

def insert_keypoints_sequence(df: pd.DataFrame, n_sample: int, kp_seq: np.ndarray) -> pd.DataFrame:
    """
    Inserta los keypoints de una muestra en un DataFrame.

    :param df: DataFrame donde se insertarán los keypoints.
    :param n_sample: ID de la muestra.
    :param kp_seq: Secuencia de keypoints de la muestra.
    :return: DataFrame actualizado con los keypoints de la muestra.
    """
    keypoints_data = [{'sample': n_sample, 'frame': frame + 1, 'keypoints': [keypoints]} for frame, keypoints in enumerate(kp_seq)]
    df_keypoints = pd.DataFrame(keypoints_data)
    return pd.concat([df, df_keypoints], ignore_index=True)

# TRAINING MODEL
def get_sequences_and_labels(words_id: List[str]) -> tuple:
    """
    Obtiene las secuencias de keypoints y sus etiquetas correspondientes.

    :param words_id: Lista de IDs de palabras.
    :return: Tupla de listas de secuencias y etiquetas.
    """
    sequences, labels = [], []
    
    for word_index, word_id in enumerate(words_id):
        hdf_path = os.path.join(KEYPOINTS_PATH, f"{word_id}.h5")
        data = pd.read_hdf(hdf_path, key='data')
        for _, df_sample in data.groupby('sample'):
            seq_keypoints = [fila['keypoints'] for _, fila in df_sample.iterrows()]
            sequences.append(seq_keypoints)
            labels.append(word_index)
                    
    return sequences, labels
