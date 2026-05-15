# 🍔 Food Analyzer

AI-powered food recognition and nutrition analysis web application built using Django and TensorFlow.

---

# 📌 Project Overview

Food Analyzer is a full-stack web application that uses Deep Learning and Computer Vision to identify food items from images and provide nutritional information such as calories, protein, fat, and carbohydrates.

Users can:

* Upload food images
* Capture food using camera
* Get AI-based predictions
* View nutrition details
* Track food history
* Analyze calorie trends
* Access dashboard analytics

---

# 🚀 Features

## 🤖 AI Food Classification

* Deep learning model trained using TensorFlow/Keras
* Supports 15 food categories
* Upload image or use live camera
* Displays prediction confidence score

## 🥗 Nutrition Analysis

Displays:

* Calories
* Protein
* Fat
* Carbohydrates

## 👤 Authentication System

* User Signup
* User Login
* Logout functionality
* Protected analyze page

## 📊 Dashboard Analytics

* Accuracy graph
* Loss graph
* Confusion matrix
* Classification metrics
* Calorie trend chart

## 🕘 History Tracking

* Stores user predictions
* Displays recent scans
* Personalized profile statistics

## 🎨 Modern UI

* Responsive design
* Professional dashboard
* Interactive charts
* Styled authentication pages
* Dynamic result cards

---

# 🧠 Model Information

## Food Classes

The model is trained on:

* carrot_cake
* chicken_curry
* chocolate_cake
* cupcakes
* donuts
* french_fries
* fried_rice
* hamburger
* hot_dog
* ice_cream
* pizza
* samosa
* spaghetti_bolognese
* steak
* sushi

## Model Performance

* Training Accuracy: ~82%
* Validation Accuracy: ~79%

## Model Format

* Saved as `.h5`

---

# 🛠️ Technologies Used

## Frontend

* HTML
* CSS
* JavaScript
* Chart.js

## Backend

* Django
* Python

## AI / ML

* TensorFlow
* Keras
* NumPy
* Matplotlib
* Scikit-learn

## Database

* SQLite

---

# 📂 Project Structure

```bash
food_analyzer_django/
│
├── analyzer_app/
│   ├── templates/
│   ├── static/
│   ├── model/
│   ├── migrations/
│   ├── views.py
│   ├── models.py
│   ├── urls.py
│   └── food_data.py
│
├── media/
├── venv/
├── manage.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/food-analyzer.git
cd food-analyzer
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Run Migrations

```bash
python manage.py migrate
```

---

## 5️⃣ Start Server

```bash
python manage.py runserver
```

---

# 🌐 Open in Browser

```bash
http://127.0.0.1:8000/
```

---

# 📈 Dashboard Includes

* Training Accuracy Graph
* Validation Accuracy Graph
* Loss Graph
* Confusion Matrix
* Classification Report
* Calorie Trends

---

# 📷 Screenshots

## Home Page

c:\Users\ADMIN\Pictures\Screenshots\Screenshot (85).pngc:\Users\ADMIN\Pictures\Screenshots\Screenshot (85).png

## Analyze Page

c:\Users\ADMIN\Pictures\Screenshots\Screenshot (51).png

## Result Page

c:\Users\ADMIN\Pictures\Screenshots\Screenshot (82).png

## Dashboard

c:\Users\ADMIN\Pictures\Screenshots\Screenshot (91).png

## Profile Page

c:\Users\ADMIN\Pictures\Screenshots\Screenshot (88).png

## Login Page
c:\Users\ADMIN\Pictures\Screenshots\Screenshot (86).png

## Sign Up Page

c:\Users\ADMIN\Pictures\Screenshots\Screenshot (87).png
---

# 🔒 Authentication Features

* Login Validation
* Signup Validation
* Secure Routes
* Session Management
* User-specific History

---

# 🧪 Future Improvements

* Add more food classes
* Improve model accuracy
* Add dark mode
* Deploy online
* Add BMI calculator
* Add food recommendations
* Add Grad-CAM visualization
* Add PDF nutrition report

---

# 📚 Learning Outcomes

This project helped in understanding:

* Deep Learning
* CNN Image Classification
* Django Full-Stack Development
* Database Integration
* REST/API Communication
* Frontend UI Design
* Model Evaluation Techniques

---

# 👨‍💻 Author

Surajsingh Dhiraj Ninad Jayesh 

Final Year AI/ML Project

---

# ⭐ Conclusion

Food Analyzer successfully combines Artificial Intelligence and Web Development to create an intelligent food recognition system with nutritional analysis and analytics dashboard.

The project demonstrates practical implementation of:

* Deep Learning
* Computer Vision
* Django Backend Development
* Interactive Frontend Design
* AI Integration in Web Applications
