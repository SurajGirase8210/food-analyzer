import os
import shutil
import random

SOURCE = "dataset/train"
DEST = "dataset/val"
SPLIT_RATIO = 0.2

for class_name in os.listdir(SOURCE):
    src_folder = os.path.join(SOURCE, class_name)
    dst_folder = os.path.join(DEST, class_name)

    os.makedirs(dst_folder, exist_ok=True)

    images = os.listdir(src_folder)
    random.shuffle(images)

    split_size = int(len(images) * SPLIT_RATIO)
    val_images = images[:split_size]

    for img in val_images:
        shutil.move(
            os.path.join(src_folder, img),
            os.path.join(dst_folder, img)
        )

print("✅ Dataset split into train/val")