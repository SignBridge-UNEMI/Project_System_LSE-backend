import os
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.src.saving.saving_api import load_model
from helpers import get_word_ids, get_sequences_and_labels
from constants import *
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

def generate_confusion_matrix():
    """
    Genera y visualiza la matriz de confusión para evaluar el rendimiento de los modelos
    de clasificación de palabras.

    La función carga modelos entrenados, prepara las secuencias de prueba, realiza
    predicciones y finalmente genera una matriz de confusión que compara las etiquetas
    verdaderas con las predicciones del modelo.
    """
    
    # Obtener los IDs de palabras a partir de un archivo de configuración
    word_ids = get_word_ids(KEYPOINTS_PATH)
    
    test_sequences, test_labels = [], []

    # Recopilar secuencias y etiquetas de prueba para cada modelo
    for model_num in MODEL_NUMS:
        # Obtener secuencias y etiquetas para un modelo específico
        test_sequences_num, test_labels_num = get_sequences_and_labels(word_ids, model_num)
        
        # Rellenar las secuencias para que tengan la misma longitud
        test_sequences_num = pad_sequences(test_sequences_num, maxlen=int(model_num), padding='pre', truncating='post', dtype='float32')
        
        test_sequences.extend(test_sequences_num)
        test_labels.extend(test_labels_num)

    all_predictions = []
    all_true_labels = []

    # Cargar los modelos desde las rutas especificadas
    models = [load_model(model_path) for model_path in MODELS_PATH]

    # Hacer predicciones para cada secuencia de prueba
    for seq, true_label in zip(test_sequences, test_labels):
        seq_length = len(seq)
        
        # Seleccionar el modelo adecuado según la longitud de la secuencia
        if seq_length <= 7:
            model = models[0]
            seq = pad_sequences([seq], maxlen=7, padding='pre', truncating='post', dtype='float32')[0]
        elif seq_length <= 12:
            model = models[1]
            seq = pad_sequences([seq], maxlen=12, padding='pre', truncating='post', dtype='float32')[0]
        else:
            model = models[2]
            seq = pad_sequences([seq], maxlen=18, padding='pre', truncating='post', dtype='float32')[0]
        
        # Realizar la predicción
        res = model.predict(np.expand_dims(seq, axis=0))[0]
        predicted_label = np.argmax(res)  # Obtener la etiqueta predicha
        
        all_predictions.append(predicted_label)
        all_true_labels.append(true_label)

    # Generar la matriz de confusión
    conf_matrix = confusion_matrix(all_true_labels, all_predictions)
    
    # Visualizar la matriz de confusión
    plt.figure(figsize=(10, 8))
    disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=word_ids)
    
    # Mostrar la matriz de confusión en un gráfico
    disp.plot(cmap=plt.cm.Blues)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.show()


if __name__ == "__main__":
    # Ejecutar la función para generar la matriz de confusión
    generate_confusion_matrix()
