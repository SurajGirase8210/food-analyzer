import os
from icrawler.builtin import BingImageCrawler

# Classes you selected
CLASSES = [
    "apple", "banana", "orange",
    "burger", "pizza", "sandwich", "french fries",
    "biryani", "dosa", "samosa", "paneer tikka",
    "rice", "pasta", "salad"
]

DATASET_PATH = "dataset/train"
IMAGES_PER_CLASS = 300   # change to 500 for better accuracy


def download_images(keyword, folder):
    os.makedirs(folder, exist_ok=True)

    crawler = BingImageCrawler(storage={"root_dir": folder})

    print(f"Downloading {keyword} images...")

    crawler.crawl(
        keyword=keyword,
        max_num=IMAGES_PER_CLASS,
        file_idx_offset=0
    )


def main():
    for food in CLASSES:
        folder_name = food.replace(" ", "_")
        folder_path = os.path.join(DATASET_PATH, folder_name)

        download_images(food, folder_path)

    print("✅ Dataset download complete!")


if __name__ == "__main__":
    main()