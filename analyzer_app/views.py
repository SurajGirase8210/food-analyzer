import os
import json
import random
import numpy as np
from PIL import Image

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.storage import default_storage

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.db.models import Sum,Count,Avg
from django.db.models.functions import TruncDate

from tensorflow.keras.models import load_model

from .forms import SignUpForm
from .models import FoodHistory
from .food_data import FOOD_DATA
from .models import UserProfile
from .food_ai_data import FOOD_AI_DATA

from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
import json

# ======================================
# CLASS LABELS
# ======================================

CLASS_NAMES = [
    "carrot_cake",
    "chicken_curry",
    "chocolate_cake",
    "cup_cakes",
    "donuts",
    "french_fries",
    "fried_rice",
    "hamburger",
    "hot_dog",
    "ice_cream",
    "pizza",
    "samosa",
    "spaghetti_bolognese",
    "steak",
    "sushi"
]


DISPLAY_NAMES = {

    "hamburger": "Burger",

    "french_fries": "French Fries",

    "fried_rice": "Fried Rice",

    "hot_dog": "Hot Dog",

    "ice_cream": "Ice Cream",

    "spaghetti_bolognese": "Spaghetti Bolognese",

    "cup_cakes": "Cup Cakes",

    "carrot_cake": "Carrot Cake",

    "chocolate_cake": "Chocolate Cake",

    "chicken_curry": "Chicken Curry",

    "samosa": "Samosa",

    "pizza": "Pizza",

    "donuts": "Donuts",

    "steak": "Steak",

    "sushi": "Sushi"
}

# ======================================
# LAZY LOAD MODEL
# ======================================

model = None


def get_model():
    global model

    if model is None:

        model_path = os.path.join(
            settings.BASE_DIR,
            "analyzer_app/model/food_model1.h5"
        )

        model = load_model(
            model_path,
            compile=False
        )

    return model


# ======================================
# IMAGE PREPROCESSING
# ======================================

def preprocess_image(image_path):

    try:
        img = Image.open(image_path).convert("RGB")

        img = img.resize((224, 224))

        img_array = np.array(img) / 255.0

        img_array = np.expand_dims(
            img_array,
            axis=0
        )

        return img_array

    except Exception:
        return None


# ======================================
# PAGES
# ======================================

def home(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


@login_required(login_url="login")
def analyze_page(request):
    return render(request, "analyze.html")


# ======================================
# PREDICTION PAGE
# ======================================

def predict(request):

    if request.method == "POST" and request.FILES.get("image"):

        uploaded_file = request.FILES["image"]

        # ----------------------------------
        # VALIDATE FILE
        # ----------------------------------

        if not uploaded_file.name.lower().endswith(
            (".png", ".jpg", ".jpeg")
        ):

            return render(request, "index.html", {
                "error": "Upload a valid image (jpg, jpeg, png)."
            })

        try:

            # ----------------------------------
            # SAVE FILE
            # ----------------------------------

            file_path = default_storage.save(
                uploaded_file.name,
                uploaded_file
            )

            full_path = os.path.join(
                settings.MEDIA_ROOT,
                file_path
            )

            # ----------------------------------
            # PREPROCESS IMAGE
            # ----------------------------------

            processed_image = preprocess_image(full_path)

            if processed_image is None:

                return render(request, "index.html", {
                    "error": "Could not process the image."
                })

            # ----------------------------------
            # MODEL PREDICTION
            # ----------------------------------

            model = get_model()

            predictions = model.predict(processed_image)

            confidence = float(np.max(predictions))

            predicted_class = CLASS_NAMES[
                np.argmax(predictions)
            ]
            ai_data = FOOD_AI_DATA.get(predicted_class, {})

            # ----------------------------------
            # TOP 3 PREDICTIONS
            # ----------------------------------

            probs = predictions[0]

            top_indices = probs.argsort()[-3:][::-1]

            top_predictions = [
                (
                    CLASS_NAMES[i],
                    float(probs[i])
                )
                for i in top_indices
            ]

            # ----------------------------------
            # NUTRITION DATA
            # ----------------------------------

            nutrition = FOOD_DATA.get(
                predicted_class,
                {}
            )

            # ----------------------------------
            # SAVE HISTORY
            # ----------------------------------

            if request.user.is_authenticated:

                FoodHistory.objects.create(
                    user=request.user,
                    food_name=predicted_class,
                    confidence=confidence,
                    calories=nutrition.get("calories"),
                    protein=nutrition.get("protein"),
                    fat=nutrition.get("fat"),
                    carbs=nutrition.get("carbs"),
                )

            # ----------------------------------
            # RETURN RESULT PAGE
            # ----------------------------------

            return render(request, "result.html", {

                "image_url": default_storage.url(file_path),

                "food_name": predicted_class,

                "confidence": round(
                    confidence * 100,
                    2
                ),

                "calories": nutrition.get("calories", 0),

                "protein": nutrition.get("protein", 0),

                "fat": nutrition.get("fat", 0),

                "carbs": nutrition.get("carbs", 0),

                "top_predictions": top_predictions,
            })

        except Exception as e:

            return render(request, "index.html", {
                "error": str(e)
            })

    return render(request, "index.html")


# ======================================
# AUTHENTICATION
# ======================================

def signup_view(request):

    if request.method == "POST":

        form = SignUpForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("analyze")

    else:

        form = SignUpForm()

    return render(request, "signup.html", {
        "form": form
    })


def login_view(request):

    form = AuthenticationForm(
        request,
        data=request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            login(
                request,
                form.get_user()
            )

            return redirect("analyze")

    return render(request, "login.html", {
        "form": form
    })


def logout_view(request):

    logout(request)

    return redirect("home")


# ======================================
# HISTORY
# ======================================

@login_required(login_url="login")
def history_view(request):

    history = (
        FoodHistory.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(request, "history.html", {
        "history": history
    })


# ======================================
# PROFILE
# ======================================

@login_required(login_url="login")
def profile_view(request):

    user = request.user

    # GET OR CREATE PROFILE
    profile, created = UserProfile.objects.get_or_create(
        user=user
    )

    # TOTAL SCANS
    total_scans = (
        FoodHistory.objects
        .filter(user=user)
        .count()
    )

    # CALORIE TREND DATA
    data = (
        FoodHistory.objects
        .filter(user=user)
        .annotate(
            date=TruncDate("created_at")
        )
        .values("date")
        .annotate(
            total_calories=Sum("calories")
        )
        .order_by("date")
    )

    dates = [
        str(item["date"])
        for item in data
    ]

    calories = [
        item["total_calories"] or 0
        for item in data
    ]

    # BMI SAVE
    if request.method == "POST":

        height = float(
            request.POST.get("height")
        )

        weight = float(
            request.POST.get("weight")
        )

        age = request.POST.get("age")

        gender = request.POST.get("gender")

        bmi = weight / ((height / 100) ** 2)

        # BMI CATEGORY
        if bmi < 18.5:

            category = "Underweight"

        elif bmi < 25:

            category = "Normal"

        elif bmi < 30:

            category = "Overweight"

        else:

            category = "Obese"

        # SAVE PROFILE
        profile.height = height

        profile.weight = weight

        profile.age = age

        profile.gender = gender

        profile.bmi = round(bmi, 1)

        profile.bmi_category = category

        profile.save()

    return render(request, "profile.html", {

        "user": user,

        "profile": profile,

        "total_scans": total_scans,

        "dates": json.dumps(dates),

        "calories": json.dumps(calories),
    })


# ======================================
# API
# ======================================
@login_required(login_url="login")
def analyze_image(request):

    print("correct analyze_image running")

    if request.method != "POST":
        return JsonResponse({
            "error": "Invalid request"
        })

    file = request.FILES.get("file")

    if not file:
        return JsonResponse({
            "error": "No image uploaded"
        })

    file_path = None

    try:

        # ======================================
        # SAVE FILE
        # ======================================

        file_path = default_storage.save(file.name, file)

        full_path = os.path.join(
            settings.MEDIA_ROOT,
            file_path
        )

        # ======================================
        # PREPROCESS IMAGE
        # ======================================

        processed_image = preprocess_image(full_path)

        if processed_image is None:
            return JsonResponse({
                "error": "Image processing failed"
            })

        # ======================================
        # MODEL PREDICTION
        # ======================================

        model = get_model()

        predictions = model.predict(processed_image)

        probs = predictions[0]

        pred_idx = np.argmax(probs)

        confidence = float(probs[pred_idx])

        predicted_class = CLASS_NAMES[pred_idx]

        display_name = DISPLAY_NAMES.get(
            predicted_class,
            predicted_class.replace("_", " ").title()
        )

        # ======================================
        # UNKNOWN FOOD CHECK
        # ======================================

        invalid_food = False

        if confidence < 0.5:
            predicted_class = "Unknown"
            invalid_food = True

        # ======================================
        # TOP PREDICTIONS
        # ======================================

        top_indices = probs.argsort()[-3:][::-1]

        top_predictions = [
            {
                "food": DISPLAY_NAMES.get(
                    CLASS_NAMES[i],
                    CLASS_NAMES[i].replace("_", " ").title()
                ),
                "confidence": round(
                    float(probs[i]) * 100,
                    2
                )
            }
            for i in top_indices
        ]

        # ======================================
        # USER PROFILE
        # ======================================

        profile = None

        if request.user.is_authenticated:
            profile = UserProfile.objects.filter(
                user=request.user
            ).first()

        # ======================================
        # BMI RECOMMENDATION
        # ======================================

        bmi_recommendation = ""
        bmi_category = ""

        if profile and profile.bmi:

            bmi_category = profile.bmi_category

            if profile.bmi_category == "Underweight":
                bmi_recommendation = (
                    "High protein foods recommended."
                )

            elif profile.bmi_category == "Normal":
                bmi_recommendation = (
                    "Maintain balanced nutrition."
                )

            elif profile.bmi_category == "Overweight":
                bmi_recommendation = (
                    "Reduce high calorie foods."
                )

            else:
                bmi_recommendation = (
                    "Prefer low fat and low sugar meals."
                )

        else:
            bmi_recommendation = (
                "Please calculate BMI first in profile section."
            )

        # ======================================
        # NUTRITION DATA
        # ======================================

        nutrition = FOOD_DATA.get(
            predicted_class,
            {}
        )

        calories = nutrition.get("calories", 0)
        protein = nutrition.get("protein", 0)
        fat = nutrition.get("fat", 0)
        carbs = nutrition.get("carbs", 0)

        # ======================================
        # SAVE HISTORY
        # ======================================

        if request.user.is_authenticated and not invalid_food:

            FoodHistory.objects.create(
                user=request.user,
                food_name=predicted_class,
                confidence=confidence,
                calories=calories,
                protein=protein,
                fat=fat,
                carbs=carbs,
            )

            # ======================================
            # TOTAL SCANS & BADGES
            # ======================================

            total_scans = FoodHistory.objects.filter(
                user=request.user
            ).count()
            
            badges = []

            if total_scans >= 1:
                badges.append("First Analysis")

            elif total_scans >= 10:
                badges.append("Food Explorer")


            elif total_scans >= 50:
                badges.append("Food Master")
                
            

        # ======================================
        # UNKNOWN FOOD RESPONSE
        # ======================================

        if invalid_food:

            return JsonResponse({

                "food": "Unknown",
                "confidence": round(confidence * 100, 2),

                "calories": 0,
                "protein": 0,
                "fat": 0,
                "carbs": 0,

                "category": "",
                "health_score": "",
                "recommendation": "",
                "insights": [],

                "top_predictions": top_predictions,

                "food_label": "",

                "bmi_recommendation": bmi_recommendation,
                "bmi_category": bmi_category,

                "diet_types": [],
                "risk_alerts": [],
                "food_suggestions": [],
                "fitness_goals": [],
                "fitness_tips": []
            })

        # ======================================
        # AI DATA
        # ======================================

        ai_data = FOOD_AI_DATA.get(
            predicted_class.lower(),
            {}
        )

        recommendation = ai_data.get(
            "recommendation",
            "Balanced nutrition recommended."
        )

        insights = ai_data.get("insights", [])
        risk_alerts = ai_data.get("risk_alerts", [])
        diet_types = ai_data.get("diet_types", [])
        similar_foods = ai_data.get("similar_foods", [])
        fitness_goals = ai_data.get("fitness_goals", [])
        fitness_tips = ai_data.get("fitness_tips", [])

        food_label = ai_data.get(
            "health_label",
            "Moderate"
        )

        food_suggestions = ai_data.get(
            "healthy_alternatives",
            []
        )

        # ======================================
        # CALORIE CATEGORY
        # ======================================

        category = "Low Calorie"

        if calories > 450:
            category = "High Calorie"

        elif calories > 250:
            category = "Medium Calorie"

        # ======================================
        # HEALTH SCORE
        # ======================================

        health_score = 85

        if fat > 20:
            health_score -= 15

        if calories > 600:
            health_score -= 15

        if protein > 20:
            health_score += 10

        if carbs > 50:
            health_score -= 5

        health_score = max(
            40,
            min(100, health_score)
        )

        # ======================================
        # JSON RESPONSE
        # ======================================

        return JsonResponse({

            "food": display_name,
            "confidence": round(confidence * 100, 2),

            "calories": calories,
            "protein": protein,
            "fat": fat,
            "carbs": carbs,

            "category": category,
            "health_score": health_score,

            "recommendation": recommendation,
            "insights": insights,

            "top_predictions": top_predictions,

            "food_label": food_label,

            "bmi_recommendation": bmi_recommendation,
            "bmi_category": bmi_category,

            "diet_types": diet_types,
            "risk_alerts": risk_alerts,

            "similar_foods": similar_foods,

            "fitness_goals": fitness_goals,
            "fitness_tips": fitness_tips,

            "food_suggestions": food_suggestions
        })

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        })

    finally:

        # ======================================
        # CLEANUP
        # ======================================

        if file_path:

            try:
                os.remove(
                    os.path.join(
                        settings.MEDIA_ROOT,
                        file_path
                    )
                )
            except Exception:
                pass


# ======================================
# RESULT PAGE
# ======================================

def result(request):

    context = {
        "image_url": "",
        "food_name": "",
        "confidence": 0,
        "calories": 250,
        "protein": 10,
        "fat": 8,
        "carbs": 30,
    }

    return render(
        request,
        "result.html",
        context
    )

# ======================================
# DASHBOARD
# ======================================

@login_required(login_url="login")
def dashboard_view(request):
    # Daily calorie totals
    daily_data = (
        FoodHistory.objects
        .filter(user=request.user)
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(total_calories=Sum("calories"))
        .order_by("date")
    )

    # Get user profile
    profile = UserProfile.objects.filter(
        user=request.user
    ).first()
    

    # Set calorie target based on BMI
    target_calories = 2200

    if profile:
        if profile.bmi_category == "Underweight":
            target_calories = 2500

        elif profile.bmi_category == "Normal":
            target_calories = 2200

        elif profile.bmi_category == "Overweight":
            target_calories = 1800

        elif profile.bmi_category == "Obese":
            target_calories = 1500

    # Today's calorie intake
    from django.utils import timezone

    today = timezone.now().date()

    today_calories = (
        FoodHistory.objects
        .filter(
            user=request.user,
            created_at__date=today
        )
        .aggregate(
            total=Sum("calories")
        )["total"] or 0
    )

    remaining_calories = max(
        target_calories - today_calories,
        0
    )

    progress = (min(
        int((today_calories / target_calories) * 100),
        100
    )if target_calories > 0 else 0)

    # Chart data
    dates = [
        str(item["date"])
        for item in daily_data
    ]

    calories = [
        item["total_calories"] or 0
        for item in daily_data
    ]

    # Top 5 most consumed foods
    food_distribution = (
        FoodHistory.objects
        .filter(user=request.user)
        .values("food_name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    food_labels = [
        item["food_name"]
        for item in food_distribution
    ]

    food_counts = [
        item["total"]
        for item in food_distribution
    ]

    # Read metrics file
    try:
        with open("static/graphs/metrics.txt", "r") as f:
            metrics_text = f.read()

    except Exception:
        metrics_text = "Metrics not available"


    user_history = FoodHistory.objects.filter(user=request.user)

    total_scans = user_history.count()
    
    badges = []
    
    if total_scans >= 1:
        badges.append("🏆 First Analysis")
    if total_scans >= 10:
        badges.append("🥗 Food Explorer")
    if total_scans >= 50:
        badges.append("🌟 Food Master")
    if total_scans >= 100:
        badges.append("🥇 Food Champion")


    total_foods = FoodHistory.objects.filter(user = request.user).count()
    
    avg_calories = FoodHistory.objects.filter(user = request.user).aggregate(avg = Avg("calories"))['avg'] or 0
    
    print("Current User:", request.user.username)
    print("Total Scans:", total_scans)
    print("Badges:", badges)

    return render(
        request,
        "dashboard.html",
        {
            "dates": json.dumps(dates),
            "calories": json.dumps(calories),
            "metrics": metrics_text,
            "food_labels": json.dumps(food_labels),
            "food_counts": json.dumps(food_counts),
            "target_calories": target_calories,
            "today_calories": today_calories,
            "remaining_calories": remaining_calories,
            "progress": progress,
            "badges": badges,
            "total_foods": total_foods,
            "avg_calories": round(avg_calories),
        },
    )