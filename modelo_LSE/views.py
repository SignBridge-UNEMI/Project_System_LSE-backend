# backend/modelo_LSE/views.py
import os
import numpy as np
from django.http import JsonResponse
from django.conf import settings
from keras.src.saving.saving_api import load_model
from .models.scripts.model import get_model
from .models.scripts.constants import LENGTH_KEYPOINTS

# Ruta al modelo entrenado (.keras o .h5)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'modelo_LSE/models/actions_15.keras')
print(f"Loading model from: {MODEL_PATH}")

# Verifica si el archivo existe
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"El archivo del modelo no se encuentra en: {MODEL_PATH}")

# Cargar el modelo
model = load_model(MODEL_PATH)

def predict_sign(request):
    if request.method == 'GET':
        # Suponiendo que el cliente envía los datos de entrada como un arreglo JSON
        keypoints_data = request.GET.getlist('keypoints')  # Los keypoints deben ser enviados en el request

        # Verifica que se hayan recibido los datos
        if not keypoints_data:
            return JsonResponse({'error': 'No se recibieron keypoints.'}, status=400)

        try:
            # Convertir los datos a float
            keypoints_data = [float(kp) for kp in keypoints_data]
            # Preprocesar los datos (convertir a numpy array y darle la forma correcta)
            input_data = np.array(keypoints_data).reshape(1, len(keypoints_data) // LENGTH_KEYPOINTS, LENGTH_KEYPOINTS)

            # Hacer la predicción
            prediction = model.predict(input_data)
            predicted_label = np.argmax(prediction, axis=1)

            # Devolver la predicción en formato JSON
            return JsonResponse({'predicted_label': int(predicted_label[0])})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido. Usa GET.'}, status=405) 
