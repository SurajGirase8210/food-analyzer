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

from django.db.models import Sum
from django.db.models.functions import TruncDate

from tensorflow.keras.models import load_model

from .forms import SignUpForm
from .models import FoodHistory
from .food_data import FOOD_DATA


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
# PREDICTION
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

            # ----------------------------------
            # RESULT
            # ----------------------------------

            if confidence < 0.6:

                result = "Not sure what this is 🤔"

            else:

                result = (
                    f"{predicted_class} "
                    f"({confidence * 100:.2f}% confident)"
                )

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

    total_scans = (
        FoodHistory.objects
        .filter(user=user)
        .count()
    )

    # ----------------------------------
    # CALORIE TREND DATA
    # ----------------------------------

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

    return render(request, "profile.html", {

        "user": user,

        "total_scans": total_scans,

        "dates": json.dumps(dates),

        "calories": json.dumps(calories),
    })


# ======================================
# API
# ======================================

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

        # ----------------------------------
        # SAVE FILE
        # ----------------------------------

        file_path = default_storage.save(
            file.name,
            file
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

            return JsonResponse({
                "error": "Image processing failed"
            })

        # ----------------------------------
        # MODEL PREDICTION
        # ----------------------------------

        model = get_model()

        predictions = model.predict(processed_image)

        probs = predictions[0]

        # ----------------------------------
        # MAIN PREDICTION
        # ----------------------------------

        pred_idx = np.argmax(probs)

        confidence = float(probs[pred_idx])

        predicted_class = CLASS_NAMES[pred_idx]

        if confidence < 0.5:
            predicted_class = "Unknown"

        # ----------------------------------
        # TOP 3 PREDICTIONS
        # ----------------------------------

        top_indices = probs.argsort()[-3:][::-1]

        top_predictions = [
            {
                "food": CLASS_NAMES[i],

                "confidence": round(
                    float(probs[i]) * 100,
                    2
                )
            }
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

        if (
            request.user.is_authenticated
            and predicted_class != "Unknown"
        ):

            FoodHistory.objects.create(
                user=request.user,
                food_name=predicted_class,
                confidence=confidence,
                calories=nutrition.get("calories"),
                protein=nutrition.get("protein"),
                fat=nutrition.get("fat"),
                carbs=nutrition.get("carbs"),
            )

        # ======================================
        # AI FEATURES
        # ======================================

        calories = nutrition.get("calories", 0)
        protein = nutrition.get("protein", 0)
        fat = nutrition.get("fat", 0)
        carbs = nutrition.get("carbs", 0)

        # ----------------------------------
        # CALORIE CATEGORY
        # ----------------------------------

        category = "Low Calorie"

        if calories > 450:
            category = "High Calorie"

        elif calories > 250:
            category = "Medium Calorie"

        # ----------------------------------
        # HEALTH SCORE
        # ----------------------------------

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

        # ----------------------------------
        # FOOD RECOMMENDATIONS
        # ----------------------------------

        recommendations = []

        if calories < 200:

            recommendations.append(
                "Light meal suitable for weight management."
            )

        if calories > 500:

            recommendations.append(
                "High calorie meal. Consume in moderation."
            )

        if protein > 20:

            recommendations.append(
                "Excellent protein source for muscle recovery."
            )

        if fat > 20:

            recommendations.append(
                "Contains high fat content. Balance with vegetables."
            )

        if carbs > 50:

            recommendations.append(
                "High carbohydrate food. Good for energy."
            )

        if calories < 300 and protein > 10:

            recommendations.append(
                "Good option for fitness-focused diets."
            )

        if fat < 10:

            recommendations.append(
                "Low fat meal suitable for heart-conscious diets."
            )

        if calories > 700:

            recommendations.append(
                "Consider smaller portions for balanced nutrition."
            )

        if not recommendations:

            recommendations.append(
                "Balanced meal with moderate nutrition values."
            )

        recommendation = random.choice(recommendations)

        # ----------------------------------
        # AI INSIGHTS
        # ----------------------------------

        insights = []

        if protein > 15:

            insights.append(
                "High protein may support muscle growth and recovery."
            )

        if fat > 20:

            insights.append(
                "This food contains elevated fat levels."
            )

        if carbs > 40:

            insights.append(
                "Rich in carbohydrates for quick energy."
            )

        if calories < 250:

            insights.append(
                "Suitable for low calorie meal plans."
            )

        if calories > 600:

            insights.append(
                "Frequent consumption may contribute to weight gain."
            )

        if fat < 10:

            insights.append(
                "Low fat composition supports healthier eating habits."
            )

        if protein > carbs:

            insights.append(
                "Protein-rich profile detected."
            )

        if carbs > protein:

            insights.append(
                "Carbohydrates are the dominant nutrient."
            )

        if health_score >= 85:

            insights.append(
                "Overall nutritional profile appears healthy."
            )

        if health_score < 60:

            insights.append(
                "Consider balancing this meal with fruits or vegetables."
            )

        if not insights:

            insights.append(
                "Moderate nutritional composition detected."
            )

        # ----------------------------------
        # JSON RESPONSE
        # ----------------------------------

        return JsonResponse({

            "food": predicted_class,

            "confidence": round(
                confidence * 100,
                2
            ),

            "calories": calories,

            "protein": protein,

            "fat": fat,

            "carbs": carbs,

            "category": category,

            "health_score": health_score,

            "recommendation": recommendation,

            "insights": insights,

            "top_predictions": top_predictions,
        })

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        })

    finally:

        # ----------------------------------
        # CLEANUP
        # ----------------------------------

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

        "image_url": image_url,

        "food_name": predicted_label,

        "confidence": round(
            confidence * 100,
            2
        ),

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

    data = (
        FoodHistory.objects
        .filter(user=request.user)
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

    metrics_text = ""

    try:

        with open(
            "static/graphs/metrics.txt",
            "r"
        ) as f:

            metrics_text = f.read()

    except Exception:

        metrics_text = "Metrics not available"

    return render(request, "dashboard.html", {

        "dates": json.dumps(dates),

        "calories": json.dumps(calories),

        "metrics": metrics_text,
    })