from PIL import Image
import os

DATASET = "C:\\Users\\ADMIN\\Desktop\\food_analyzer_django\\analyzer_app\\dataset\\train"

for class_name in os.listdir(DATASET):
    folder = os.path.join(DATASET, class_name)

    for img_name in os.listdir(folder):
        path = os.path.join(folder, img_name)

        try:
            img = Image.open(path)
            img.verify()
        except:
            os.remove(path)

print("✅ Broken images removed")