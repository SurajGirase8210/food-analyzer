import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Food classes (must match your dataset folder names)
classes = ["apple fruit", "banana fruit", "burger", "pizza", "salad food"]

# Load trained model
model = load_model("food_model.h5")

# Load test image
img_path = "test.jpg"   # put a food image with this name in the same folder
img = image.load_img("dataset/train/banana fruit/000035.jpg", target_size=(224, 224))

# Convert image to array
img_array = image.img_to_array(img)

# Normalize image
img_array = img_array / 255.0

# Expand dimensions for model input
img_array = np.expand_dims(img_array, axis=0)

# Predict
prediction = model.predict(img_array)

# Get predicted class index
predicted_index = np.argmax(prediction)

# Get food name
predicted_food = classes[predicted_index]

print("Prediction:", predicted_food)
print("Confidence:", prediction[0][predicted_index])