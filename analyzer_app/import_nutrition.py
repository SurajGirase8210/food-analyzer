import csv
import os
from analyzer_app.models import Nutrition
from django.conf import settings

def run():
    file_path = os.path.join(
        settings.BASE_DIR,
        'analyzer_app',
        'data',
        'nutrition.csv'
    )

    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Nutrition.objects.update_or_create(
                food=row['food'].strip(),
                defaults={
                    'calories': float(row['calories']),
                    'protein': float(row['protein']),
                    'fat': float(row['fat']),
                    'carbs': float(row['carbs'])
                }
            )

    print("✅ Nutrition database populated successfully")
