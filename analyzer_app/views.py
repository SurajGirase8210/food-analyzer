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
        model_path = os.path.join(settings.BASE_DIR, "analyzer_app/model/food_model.h5")
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

            return render(request, "index.html", {
                "result": result,
                "confidence": f"{confidence*100:.2f}%",
                "top_predictions": top_predictions,
                "nutrition": nutrition,
                "image_url": os.path.join(settings.MEDIA_URL, file_path)
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

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def profile_view(request):
    user = request.user

    # basic stats
    total_scans = FoodHistory.objects.filter(user=user).count()

    return render(request, "profile.html", {
        "user": user,
        "total_scans": total_scans
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


# import traceback

# def analyze_image(request):
#     print("🔥 CORRECT ANALYZE_IMAGE RUNNING")

#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"})

#     file = request.FILES.get("file")

#     if not file:
#         return JsonResponse({"error": "No image uploaded"})

#     try:
#         file_path = default_storage.save(file.name, file)
#         full_path = os.path.join(settings.MEDIA_ROOT, file_path)

#         processed_image = preprocess_image(full_path)
#         if processed_image is None:
#             return JsonResponse({"error": "Image processing failed"})

#         model = get_model()
#         predictions = model.predict(processed_image)

#         probs = predictions[0]

#         pred_idx = np.argmax(probs)
#         confidence = float(probs[pred_idx])
#         predicted_class = CLASS_NAMES[pred_idx]

#         return JsonResponse({
#             "food": predicted_class,
#             "confidence": round(confidence * 100, 2)
#         })

#     except Exception as e:
#         print("🔥 ERROR OCCURRED:")
#         traceback.print_exc()   # 🔥 THIS IS KEY
#         return JsonResponse({"error": str(e)})