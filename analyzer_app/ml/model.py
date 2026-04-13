import tensorflow as tf
import numpy as np
from PIL import Image

# Load model once (IMPORTANT for performance)
model = tf.keras.applications.MobileNetV2(
    weights="imagenet",
    include_top=True
)

def predict_food(image_file):
    image = Image.open(image_file).convert("RGB")
    image = image.resize((224, 224))

    img_array = np.array(image)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array)
    decoded = tf.keras.applications.mobilenet_v2.decode_predictions(
        predictions, top=1
    )[0][0]

    # decoded = (class_id, label, confidence)
    food_label = decoded[1]
    confidence = float(decoded[2])

    return food_label, confidence
