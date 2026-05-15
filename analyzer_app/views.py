import os
import numpy as np
from PIL import Image

from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import JsonResponse

from tensorflow.keras.models import load_model

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from .forms import SignUpForm
from .models import FoodHistory
from .food_data import FOOD_DATA

# Class labels
CLASS_NAMES = [
    "carrot_cake","chicken_curry","chocolate_cake","cup_cakes",
    "donuts","french_fries","fried_rice","hamburger",
    "hot_dog","ice_cream","pizza","samosa",
    "spaghetti_bolognese","steak","sushi"
]

# Lazy load model
model = None

# from tensorflow.keras.models import load_model

def get_model():
    global model
    if model is None:
        model_path = os.path.join(settings.BASE_DIR, "analyzer_app/model/food_model1.h5")
        model = load_model(model_path, compile=False)  # ✅ FIX
    return model


def preprocess_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception:
        return None


# =======================
# Pages
# =======================

def home(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


@login_required(login_url='login')
def analyze_page(request):
    return render(request, "analyze.html")


# =======================
# Prediction
# =======================

def predict(request):
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]

        # Validate file
        if not uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg")):
            return render(request, "index.html", {
                "error": "Upload a valid image (jpg, jpeg, png)."
            })

        try:
            # Save file
            file_path = default_storage.save(uploaded_file.name, uploaded_file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Preprocess
            processed_image = preprocess_image(full_path)
            if processed_image is None:
                return render(request, "index.html", {
                    "error": "Could not process the image."
                })

            # Predict
            model = get_model()
            predictions = model.predict(processed_image)

            confidence = float(np.max(predictions))
            predicted_class = CLASS_NAMES[np.argmax(predictions)]

            # Result
            if confidence < 0.6:
                result = "Not sure what this is 🤔"
            else:
                result = f"{predicted_class} ({confidence*100:.2f}% confident)"

            # Top 3 predictions
            probs = predictions[0]
            top_indices = probs.argsort()[-3:][::-1]

            top_predictions = [
                (CLASS_NAMES[i], float(probs[i]))
                for i in top_indices
            ]

            # Nutrition data
            nutrition = FOOD_DATA.get(predicted_class, {})

            # Save history
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

            return render(request, "result.html", {
                "image_url":  default_storage.url(file_path),
                "food_name": predicted_class,
                "confidence": round(confidence * 100, 2),

                "calories": nutrition.get("calories", 0),
                "protein": nutrition.get("protein", 0),
                "fat": nutrition.get("fat", 0),
                "carbs": nutrition.get("carbs", 0)
            })

        except Exception as e:
            return render(request, "index.html", {
                "error": str(e)
            })

    return render(request, "index.html")


# =======================
# Auth
# =======================

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('analyze')
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            return redirect('analyze')

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('home')


# =======================
# History
# =======================

@login_required(login_url='login')
def history_view(request):
    history = FoodHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "history.html", {"history": history})


# =======================
# My Profile
# =======================

from django.db.models import Sum
from django.db.models.functions import TruncDate
import json

@login_required(login_url='login')
def profile_view(request):

    user = request.user

    total_scans = FoodHistory.objects.filter(user=user).count()

    # Calorie trend data
    data = (
        FoodHistory.objects
        .filter(user=user)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(total_calories=Sum('calories'))
        .order_by('date')
    )

    dates = [str(item['date']) for item in data]
    calories = [item['total_calories'] or 0 for item in data]

    return render(request, "profile.html", {
        "user": user,
        "total_scans": total_scans,
        "dates": json.dumps(dates),
        "calories": json.dumps(calories),
    })
# =======================
# API (Optional)
# =======================

from django.http import JsonResponse
import os
import numpy as np
from django.conf import settings
from django.core.files.storage import default_storage

def analyze_image(request):
    print("correct analyze_image running")
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"})

    file = request.FILES.get("file")

    if not file:
        return JsonResponse({"error": "No image uploaded"})

    file_path = None  # for safe cleanup

    try:
        # ---------- SAVE FILE ----------
        file_path = default_storage.save(file.name, file)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # ---------- PREPROCESS ----------
        processed_image = preprocess_image(full_path)
        if processed_image is None:
            return JsonResponse({"error": "Image processing failed"})

        # ---------- MODEL ----------
        model = get_model()
        predictions = model.predict(processed_image)

        probs = predictions[0]

        # ---------- MAIN PREDICTION ----------
        pred_idx = np.argmax(probs)
        confidence = float(probs[pred_idx])
        predicted_class = CLASS_NAMES[pred_idx]

        if confidence < 0.5:
            predicted_class = "Unknown"

        # ---------- TOP 3 ----------
        top_indices = probs.argsort()[-3:][::-1]

        top_predictions = [
            {
                "food": CLASS_NAMES[i],
                "confidence": round(float(probs[i]) * 100, 2)
            }
            for i in top_indices
        ]

        # ---------- NUTRITION ----------
        nutrition = FOOD_DATA.get(predicted_class, {})

        # ---------- SAVE HISTORY ----------
        if request.user.is_authenticated and predicted_class != "Unknown":
            FoodHistory.objects.create(
                user=request.user,
                food_name=predicted_class,
                confidence=confidence,
                calories=nutrition.get("calories"),
                protein=nutrition.get("protein"),
                fat=nutrition.get("fat"),
                carbs=nutrition.get("carbs"),
            )

        # ---------- RESPONSE ----------
        return JsonResponse({
            "food": predicted_class,
            "confidence": round(confidence * 100, 2),
            "calories": nutrition.get("calories"),
            "protein": nutrition.get("protein"),
            "fat": nutrition.get("fat"),
            "carbs": nutrition.get("carbs"),
            "top_predictions": top_predictions
        })

    except Exception as e:
        return JsonResponse({"error": str(e)})

    finally:
        # ---------- CLEANUP ----------
        if file_path:
            try:
                os.remove(os.path.join(settings.MEDIA_ROOT, file_path))
            except:
                pass


def result(request):
    context = {
        "image_url": image_url,  # path to uploaded image
        "food_name": predicted_label,
        "confidence": round(confidence * 100, 2),

        "calories": 250,
        "protein": 10,
        "fat": 8,
        "carbs": 30
    }

    return render(request, "result.html", context)


from django.db.models import Sum
from django.db.models.functions import TruncDate
import json

@login_required(login_url='login')
def dashboard_view(request):

    data = (
        FoodHistory.objects
        .filter(user=request.user)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(total_calories=Sum('calories'))
        .order_by('date')
    )

    dates = [str(item['date']) for item in data]
    calories = [item['total_calories'] or 0 for item in data]

    metrics_text = ""

    try:
        with open("static/graphs/metrics.txt", "r") as f:
            metrics_text = f.read()
    except:
        metrics_text = "Metrics not available"

    return render(request, "dashboard.html", {
        "dates": json.dumps(dates),
        "calories": json.dumps(calories),
        "metrics": metrics_text
    })