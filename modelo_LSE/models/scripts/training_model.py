import numpy as np
from model import get_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from helpers import get_word_ids, get_sequences_and_labels
from constants import *

def training_model(model_path, epochs=500):
    """
    Entrena un modelo de aprendizaje automático para reconocer palabras a partir de secuencias de datos.

    Parámetros:
    - model_path (str): Ruta donde se guardará el modelo entrenado.
    - epochs (int): Número de épocas para entrenar el modelo (por defecto es 500).

    El modelo se entrena utilizando datos de secuencias y etiquetas obtenidos de archivos JSON.
    Se implementa la parada temprana para evitar el sobreajuste y se guarda el modelo al final.
    """
    # Obtener IDs de palabras de un archivo JSON
    word_ids = get_word_ids(WORDS_JSON_PATH)  # ['word1', 'word2', 'word3']

    # Obtener secuencias y etiquetas a partir de los IDs de palabras
    sequences, labels = get_sequences_and_labels(word_ids)

    # Rellenar secuencias para que tengan la misma longitud
    sequences = pad_sequences(sequences, maxlen=int(MODEL_FRAMES), padding='pre', truncating='post', dtype='float16')

    # Convertir las secuencias y etiquetas a matrices numpy
    X = np.array(sequences)  # Datos de entrada
    y = to_categorical(labels).astype(int)  # Etiquetas categóricas

    # Configurar la parada temprana
    early_stopping = EarlyStopping(monitor='accuracy', patience=10, restore_best_weights=True)

    # Dividir los datos en conjuntos de entrenamiento y validación
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.05, random_state=42)

    # Obtener el modelo a partir de una función externa
    model = get_model(int(MODEL_FRAMES), len(word_ids))

    # Entrenar el modelo
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, batch_size=8, callbacks=[early_stopping])

    # Mostrar un resumen del modelo
    model.summary()

    # Guardar el modelo entrenado en la ruta especificada
    model.save(model_path)

if __name__ == "__main__":
    # Ejecutar la función de entrenamiento y guardar el modelo
    training_model(MODEL_PATH)
