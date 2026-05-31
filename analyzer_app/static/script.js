console.log("Script loaded");

document.addEventListener("DOMContentLoaded", function () {
  /* ---------- ELEMENTS ---------- */

  const uploadForm = document.getElementById("uploadForm");

  // Stop script on pages where analyze form doesn't exist
  if (!uploadForm) return;

  const resultDiv = document.getElementById("result");

  const resultImage = document.getElementById("resultImage");

  const fileInput = document.querySelector('input[type="file"]');

  const preview = document.getElementById("preview");

  const cameraBtn = document.getElementById("cameraBtn");

  const video = document.getElementById("cameraPreview");

  const captureBtn = document.getElementById("captureBtn");

  const canvas = document.getElementById("cameraCanvas");

  const manualForm = document.getElementById("manualForm");

  const manualResult = document.getElementById("manualResult");

  const manualText = document.getElementById("manualText");

  const loader = document.getElementById("loader");

  let stream = null;

  let isProcessing = false;

  /* ---------- CSRF ---------- */

  function getCSRFToken() {
    const token = document.querySelector("[name=csrfmiddlewaretoken]");

    return token ? token.value : "";
  }

  /* ---------- UI HELPERS ---------- */

  function showLoading() {
    if (loader) {
      loader.classList.remove("hidden");
    }

    if (resultDiv) {
      resultDiv.classList.remove("hidden");

      resultDiv.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }

    document.getElementById("foodTitle").innerText = "Analyzing...";
  }

  function showError(msg) {
    if (loader) {
      loader.classList.add("hidden");
    }

    if (resultDiv) {
      resultDiv.classList.remove("hidden");
    }

    const foodTitle = document.getElementById("foodTitle");

    const recommendationText = document.getElementById("recommendationText");

    if (foodTitle) {
      foodTitle.innerText = "Error";
    }

    if (recommendationText) {
      recommendationText.innerText = msg;
    }
  }

  function showResult(data) {
    if (loader) {
      loader.classList.add("hidden");
    }

    if (resultDiv) {
      resultDiv.classList.remove("hidden");
    }

    if (data.error) {
      showError(data.error);
      return;
    }

    const invalidFood =
      !data.food || data.food.toLowerCase().includes("unknown");

    /* BASIC INFO */

    const foodTitle = document.getElementById("foodTitle");
    const confidenceText = document.getElementById("confidenceText");
    const categoryText = document.getElementById("categoryText");
    const healthScore = document.getElementById("healthScore");
    const caloriesText = document.getElementById("caloriesText");
    const proteinText = document.getElementById("proteinText");
    const fatText = document.getElementById("fatText");
    const carbsText = document.getElementById("carbsText");
    const recommendationText = document.getElementById("recommendationText");

    if (foodTitle) {
      foodTitle.innerText = invalidFood ? "Unknown Food" : data.food;
    }

    if (confidenceText) {
      confidenceText.innerText = (data.confidence || 0) + "%";
    }

    if (categoryText) {
      categoryText.innerText = data.category || "Normal";
    }

    if (healthScore) {
      healthScore.innerText = data.health_score || "80";
    }

    if (caloriesText) {
      caloriesText.innerText = data.calories || "0";
    }

    if (proteinText) {
      proteinText.innerText = (data.protein || 0) + " g";
    }

    if (fatText) {
      fatText.innerText = (data.fat || 0) + " g";
    }

    if (carbsText) {
      carbsText.innerText = (data.carbs || 0) + " g";
    }

    if (recommendationText) {
      recommendationText.innerText =
        data.recommendation || "Eat in moderation and stay hydrated.";
    }

    /* AI INSIGHTS */

    const insightsList = document.getElementById("insightsList");

    if (insightsList) {
      insightsList.innerHTML = "";

      if (data.insights && data.insights.length > 0) {
        data.insights.forEach((item) => {
          insightsList.innerHTML += `
          <li>${item}</li>
        `;
        });
      } else {
        insightsList.innerHTML = "<li>No AI insights available</li>";
      }
    }

    /* TOP PREDICTIONS */

    const topPredictions = document.getElementById("topPredictions");

    if (topPredictions) {
      topPredictions.innerHTML = "";

      if (data.top_predictions && data.top_predictions.length > 0) {
        data.top_predictions.forEach((item) => {
          topPredictions.innerHTML += `
          <div class="prediction-row">
            <span>${item.food}</span>
            <span>${item.confidence}%</span>
          </div>
        `;
        });
      } else {
        topPredictions.innerHTML = "<p>No predictions available</p>";
      }
    }

    /* HEALTH LABEL */

    const foodLabel = document.getElementById("foodLabel");

    if (foodLabel) {
      foodLabel.innerText = data.food_label || "Healthy";
    }

    /* BMI RECOMMENDATION */

    const bmiRecommendation = document.getElementById("bmiRecommendation");

    if (bmiRecommendation) {
      bmiRecommendation.innerText =
        data.bmi_recommendation || "Maintain a balanced diet.";
    }

    /* DIET TYPES */

    const dietList = document.getElementById("dietList");

    if (dietList) {
      dietList.innerHTML = "";

      if (data.diet_types && data.diet_types.length > 0) {
        data.diet_types.forEach((item) => {
          dietList.innerHTML += `
          <li>${item}</li>
        `;
        });
      } else {
        dietList.innerHTML = "<li>No diet compatibility found</li>";
      }
    }

    /* HEALTHY ALTERNATIVES */

    const foodSuggestions = document.getElementById("foodSuggestions");

    if (foodSuggestions) {
      foodSuggestions.innerHTML = "";

      if (data.food_suggestions && data.food_suggestions.length > 0) {
        data.food_suggestions.forEach((item) => {
          foodSuggestions.innerHTML += `
                <li>${item}</li>
            `;
        });
      } else {
        foodSuggestions.innerHTML =
          "<li>No healthy alternatives available</li>";
      }
    }

    /* SIMILAR FOODS */

const similarFoods =
    document.getElementById("similarFoods");

if (similarFoods) {

    similarFoods.innerHTML = "";

    if (
        data.similar_foods &&
        data.similar_foods.length > 0
    ) {

        data.similar_foods.forEach((item) => {

            similarFoods.innerHTML += `
                <li>${item}</li>
            `;

        });

    } else {

        similarFoods.innerHTML =
            "<li>No similar foods available</li>";
    }
}

    /* RISK ALERTS */

    const riskAlerts = document.getElementById("riskAlerts");

    if (riskAlerts) {
      riskAlerts.innerHTML = "";

      if (data.risk_alerts && data.risk_alerts.length > 0) {
        data.risk_alerts.forEach((item) => {
          riskAlerts.innerHTML += `
          <li>${item}</li>
        `;
        });
      } else {
        riskAlerts.innerHTML = "<li>No health risks detected</li>";
      }
    }

    
    /* FITNESS GOALS */

const fitnessGoals =
    document.getElementById("fitnessGoals");

if (fitnessGoals) {

    fitnessGoals.innerHTML = "";

    if (
        data.fitness_goals &&
        data.fitness_goals.length > 0
    ) {

        data.fitness_goals.forEach((item) => {

            fitnessGoals.innerHTML += `
                <li>${item}</li>
            `;

        });

    } else {

        fitnessGoals.innerHTML =
            "<li>No fitness goals available</li>";
    }
}


/* FITNESS TIPS */

const fitnessTips =
    document.getElementById("fitnessTips");

if (fitnessTips) {

    fitnessTips.innerHTML = "";

    if (
        data.fitness_tips &&
        data.fitness_tips.length > 0
    ) {

        data.fitness_tips.forEach((item) => {

            fitnessTips.innerHTML += `
                <li>${item}</li>
            `;

        });

    } else {

        fitnessTips.innerHTML =
            "<li>No fitness tips available</li>";
    }
}
    /* CLEAR OUTPUTS FOR UNKNOWN FOOD */

    if (invalidFood) {
      document.getElementById("foodLabel").innerText = "-";

      document.getElementById("bmiRecommendation").innerText = "-";

      document.getElementById("recommendationText").innerText = "-";

      document.getElementById("categoryText").innerText = "-";

      document.getElementById("healthScore").innerText = "-";

      document.getElementById("dietList").innerHTML = "";

      document.getElementById("riskAlerts").innerHTML = "";

      document.getElementById("foodSuggestions").innerHTML = "";

      document.getElementById("fitnessGoals").innerHTML = "";

      document.getElementById("insightsList").innerHTML = "";

      return;
    }
  }

  /* ---------- IMAGE UPLOAD ---------- */

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (isProcessing) return;

    isProcessing = true;

    showLoading();

    try {
      const formData = new FormData(uploadForm);

      const file = fileInput.files[0];

      if (file && resultImage) {
        resultImage.src = URL.createObjectURL(file);

        resultImage.classList.remove("hidden");
      }

      const res = await fetch("/analyze/do/", {
        method: "POST",

        headers: {
          "X-CSRFToken": getCSRFToken(),
        },

        body: formData,
      });

      const data = await res.json();

      showResult(data);
    } catch (err) {
      console.error(err);

      showError("Upload failed.");
    } finally {
      isProcessing = false;
    }
  });

  /* ---------- IMAGE PREVIEW ---------- */

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];

      if (!file) {
        if (preview) {
          preview.classList.add("hidden");
        }

        return;
      }

      const reader = new FileReader();

      reader.onload = (e) => {
        if (preview) {
          preview.src = e.target.result;

          preview.classList.remove("hidden");
        }
      };

      reader.readAsDataURL(file);
    });
  }

  /* ---------- CAMERA OPEN ---------- */

  if (cameraBtn) {
    cameraBtn.addEventListener("click", async () => {
      try {
        stopCamera();

        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: "environment",
          },
        });

        video.srcObject = stream;

        video.classList.remove("hidden");

        captureBtn.classList.remove("hidden");
      } catch (err) {
        console.error(err);

        alert("Camera not accessible");
      }
    });
  }

  /* ---------- CAMERA CAPTURE ---------- */

  if (captureBtn) {
    captureBtn.addEventListener("click", () => {
      if (isProcessing) return;

      isProcessing = true;

      captureBtn.disabled = true;

      const ctx = canvas.getContext("2d");

      canvas.width = 224;

      canvas.height = 224;

      ctx.drawImage(video, 0, 0, 224, 224);

      canvas.toBlob(async (blob) => {
        if (!blob) {
          showError("Capture failed");

          resetCamera();

          return;
        }

        if (resultImage) {
          resultImage.src = URL.createObjectURL(blob);

          resultImage.classList.remove("hidden");
        }

        showLoading();

        try {
          const formData = new FormData();

          formData.append("file", blob, "camera.jpg");

          const res = await fetch("/analyze/do/", {
            method: "POST",

            headers: {
              "X-CSRFToken": getCSRFToken(),
            },

            body: formData,
          });

          const data = await res.json();

          showResult(data);
        } catch (err) {
          console.error(err);

          showError("Camera failed.");
        }

        stopCamera();

        resetCamera();
      }, "image/jpeg");
    });
  }

  /* ---------- STOP CAMERA ---------- */

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());

      stream = null;
    }
  }

  /* ---------- RESET CAMERA ---------- */

  function resetCamera() {
    if (video) {
      video.classList.add("hidden");
    }

    if (captureBtn) {
      captureBtn.classList.add("hidden");

      captureBtn.disabled = false;
    }

    isProcessing = false;
  }

  /* ---------- MANUAL ENTRY ---------- */

  if (manualForm) {
    manualForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const food = document.getElementById("foodName").value;

      const qty = parseFloat(document.getElementById("foodQty").value);

      if (!food || !qty) {
        return;
      }

      /* -----------------------------
       BASIC CALCULATIONS
    ----------------------------- */

      const calories = Math.round(qty * 1.5);

      const protein = Math.round(qty * 0.08);

      const fat = Math.round(qty * 0.04);

      const carbs = Math.round(qty * 0.2);

      /* -----------------------------
       CATEGORY
    ----------------------------- */

      let category = "Low Calorie";

      if (calories > 500) {
        category = "High Calorie";
      } else if (calories > 250) {
        category = "Medium Calorie";
      }

      /* -----------------------------
       HEALTH SCORE
    ----------------------------- */

      let healthScore = 80;

      if (fat > 20) {
        healthScore -= 10;
      }

      if (protein > 20) {
        healthScore += 10;
      }

      healthScore = Math.max(40, Math.min(100, healthScore));

      /* -----------------------------
       HEALTH LABEL
    ----------------------------- */

      let foodLabel = "Healthy Choice";

      if (calories > 600 || fat > 25) {
        foodLabel = "Unhealthy";
      } else if (calories > 350) {
        foodLabel = "Moderate";
      }

      /* -----------------------------
       RECOMMENDATION
    ----------------------------- */

      let recommendation = "Balanced nutrition recommended.";

      if (calories < 250) {
        recommendation = "Light meal suitable for weight management.";
      }

      if (protein > 20) {
        recommendation = "Excellent protein source for fitness diets.";
      }

      /* -----------------------------
       INSIGHTS
    ----------------------------- */

      const insights = [];

      if (protein > 15) {
        insights.push("High protein content detected.");
      }

      if (fat > 20) {
        insights.push("Contains elevated fat levels.");
      }

      if (calories < 250) {
        insights.push("Suitable for low calorie meal plans.");
      }

      if (insights.length === 0) {
        insights.push("Moderate nutritional profile detected.");
      }

      /* -----------------------------
       SHOW SAME RESULT UI
    ----------------------------- */

      resultDiv.classList.remove("hidden");

      resultDiv.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

      document.getElementById("foodTitle").innerText = food;

      document.getElementById("confidenceText").innerText = "Manual Entry";

      document.getElementById("caloriesText").innerText = calories;

      document.getElementById("proteinText").innerText = protein + " g";

      document.getElementById("fatText").innerText = fat + " g";

      document.getElementById("carbsText").innerText = carbs + " g";

      document.getElementById("healthScore").innerText = healthScore;

      document.getElementById("categoryText").innerText = category;

      document.getElementById("foodLabel").innerText = foodLabel;

      document.getElementById("recommendationText").innerText = recommendation;

      /* BMI */

      const bmiText = document.getElementById("bmiRecommendation");

      if (bmiText) {
        bmiText.innerText =
          "BMI recommendations available after BMI calculation.";
      }

      /* INSIGHTS */

      const insightsList = document.getElementById("insightsList");

      insightsList.innerHTML = "";

      insights.forEach((item) => {
        insightsList.innerHTML += `
            <li>${item}</li>
        `;
      });

      /* HEALTHY ALTERNATIVES */

      const foodSuggestions = document.getElementById("foodSuggestions");

      if (foodSuggestions) {
        foodSuggestions.innerHTML = `

    <li>Fresh Salad</li>

    <li>Fruit Bowl</li>

    <li>Protein Smoothie</li>

  `;
      }

      /* FITNESS TIPS */

      const fitnessTips = document.getElementById("fitnessTips");

      if (fitnessTips) {
        fitnessTips.innerHTML = `

    <li>Maintain regular exercise.</li>

    <li>Stay hydrated throughout the day.</li>

    <li>Balance meals with protein and fiber.</li>

  `;
      }

      /* TOP PREDICTIONS */

      const topPredictions = document.getElementById("topPredictions");

      topPredictions.innerHTML = `
        <div class="prediction-row">
            <span>${food}</span>
            <span>Manual</span>
        </div>
    `;
    });

    /* ---------- PROFILE DROPDOWN ---------- */

    function toggleDropdown() {
      const menu = document.getElementById("dropdownMenu");

      if (menu) {
        menu.classList.toggle("show");
      }
    }

    window.addEventListener("click", function (e) {
      const dropdown = document.querySelector(".profile-dropdown");

      if (dropdown && !dropdown.contains(e.target)) {
        const menu = document.getElementById("dropdownMenu");

        if (menu) {
          menu.classList.remove("show");
        }
      }
    });

    const profileBtn = document.getElementById("profileBtn");

    const dropdownMenu = document.getElementById("dropdownMenu");

    if (profileBtn) {
      profileBtn.addEventListener("click", function (e) {
        e.stopPropagation();

        if (dropdownMenu) {
          dropdownMenu.classList.toggle("show");
        }
      });
    }

    document.addEventListener("click", function () {
      if (dropdownMenu) {
        dropdownMenu.classList.remove("show");
      }
    });
  }
});
