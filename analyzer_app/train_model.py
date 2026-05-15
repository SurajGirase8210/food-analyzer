




import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# =========================
# CONFIG
# =========================
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
DATA_DIR = "C:\\Users\\ADMIN\\Desktop\\food_analyzer_django\\analyzer_app\\dataset\\train"

OUTPUT_DIR = "C:\\Users\\ADMIN\\Desktop\\food_analyzer_django\\analyzer_app\\static\\graphs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# DATA GENERATOR
# =========================
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

train_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

NUM_CLASSES = len(train_gen.class_indices)

# =========================
# MODEL
# =========================
base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)

base_model.trainable = False

x = base_model.output
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(128, activation='relu')(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)

model = models.Model(inputs=base_model.input, outputs=outputs)

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# =========================
# TRAIN
# =========================
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS
)

# =========================
# SAVE MODEL
# =========================
model.save("new_food_model.h5")

# =========================
# GRAPHS
# =========================
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

# Accuracy graph
plt.figure()
plt.plot(acc)
plt.plot(val_acc)
plt.title("Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend(["Train", "Val"])
plt.savefig(os.path.join(OUTPUT_DIR, "accuracy.png"))
plt.close()

# Loss graph
plt.figure()
plt.plot(loss)
plt.plot(val_loss)
plt.title("Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend(["Train", "Val"])
plt.savefig(os.path.join(OUTPUT_DIR, "loss.png"))
plt.close()

# =========================
# EVALUATION
# =========================
y_true = val_gen.classes
y_pred = model.predict(val_gen)
y_pred_classes = np.argmax(y_pred, axis=1)

accuracy = accuracy_score(y_true, y_pred_classes)
report = classification_report(y_true, y_pred_classes)

# Save metrics
with open(os.path.join(OUTPUT_DIR, "metrics.txt"), "w") as f:
    f.write(f"Accuracy: {accuracy * 100:.2f}%\n\n")
    f.write(report)

# =========================
# CONFUSION MATRIX
# =========================
cm = confusion_matrix(y_true, y_pred_classes)

plt.figure(figsize=(10,8))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=list(val_gen.class_indices.keys()),
    yticklabels=list(val_gen.class_indices.keys())
)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")

plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix.png"))
plt.close()

print("✅ Training + Evaluation Completed")