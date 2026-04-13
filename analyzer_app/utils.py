import numpy as np
import json
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# Load class names
with open("analyzer_app/model/classes.json") as f:
    class_indices = json.load(f)

# Sort classes properly
CLASS_NAMES = [k for k, v in sorted(class_indices.items(), key=lambda x: x[1])]

# 🔥 Load FULL trained model (no rebuilding)
# model = load_model("food_analyzer_django/analyzer_app/model/food_model.h5",
#                    compile=False)  # Set compile=False to avoid issues with custom objects


def predict_food(img_file):
    img = Image.open(img_file).convert("RGB")
    img = img.resize((224, 224))

    img_array = np.array(img)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0]

    # Top 1 prediction
    top_index = np.argmax(prediction)

    food_name = CLASS_NAMES[top_index]
    confidence = round(float(prediction[top_index]) * 100, 2)

    return [{
        "food": food_name,
        "confidence": confidence
    }]
    
from .views import get_model

def predict_food(processed_image):
    model = get_model()
    predictions = model.predict(processed_image)
    return predictions