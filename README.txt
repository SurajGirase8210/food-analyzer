Food Analyzer Django (converted from Flask demo)

Quick start (on your machine):
1. Create a virtualenv and activate it.
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py runserver
5. Open http://127.0.0.1:8000/ in your browser.

Notes:
- The analyze endpoint uses a dummy random predictor (no ML model required).
- Static files are included under analyzer_app/static.
- Replace image placeholders in analyzer_app/static/images with your actual images.
