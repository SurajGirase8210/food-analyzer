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
    const token = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    );

    return token ? token.value : "";
  }

  /* ---------- UI HELPERS ---------- */

  function showLoading() {

    if (resultDiv) {
      resultDiv.classList.remove("hidden");
    }

    if (loader) {
      loader.classList.remove("hidden");
    }

    const foodTitle =
      document.getElementById("foodTitle");

    if (foodTitle) {
      foodTitle.innerText = "Analyzing...";
    }
  }

  function showError(msg) {

    if (loader) {
      loader.classList.add("hidden");
    }

    if (resultDiv) {
      resultDiv.classList.remove("hidden");
    }

    const foodTitle =
      document.getElementById("foodTitle");

    const recommendationText =
      document.getElementById("recommendationText");

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

    const foodTitle =
      document.getElementById("foodTitle");

    const confidenceText =
      document.getElementById("confidenceText");

    const categoryText =
      document.getElementById("categoryText");

    const healthScore =
      document.getElementById("healthScore");

    const caloriesText =
      document.getElementById("caloriesText");

    const proteinText =
      document.getElementById("proteinText");

    const fatText =
      document.getElementById("fatText");

    const carbsText =
      document.getElementById("carbsText");

    const recommendationText =
      document.getElementById("recommendationText");

    if (foodTitle) {
      foodTitle.innerText = data.food;
    }

    if (confidenceText) {
      confidenceText.innerText =
        data.confidence + "%";
    }

    if (categoryText) {
      categoryText.innerText =
        data.category || "Normal";
    }

    if (healthScore) {
      healthScore.innerText =
        data.health_score || "80";
    }

    if (caloriesText) {
      caloriesText.innerText =
        data.calories ?? "N/A";
    }

    if (proteinText) {
      proteinText.innerText =
        (data.protein ?? "N/A") + " g";
    }

    if (fatText) {
      fatText.innerText =
        (data.fat ?? "N/A") + " g";
    }

    if (carbsText) {
      carbsText.innerText =
        (data.carbs ?? "N/A") + " g";
    }

    if (recommendationText) {
      recommendationText.innerText =
        data.recommendation ||
        "Eat in moderation and stay hydrated.";
    }

    /* ---------- AI INSIGHTS ---------- */

    const insightsList =
      document.getElementById("insightsList");

    if (
      insightsList &&
      data.insights
    ) {

      insightsList.innerHTML = "";

      data.insights.forEach(item => {

        insightsList.innerHTML += `
          <li>${item}</li>
        `;
      });
    }

    /* ---------- TOP PREDICTIONS ---------- */

    const topPredictions =
      document.getElementById("topPredictions");

    if (
      topPredictions &&
      data.top_predictions
    ) {

      topPredictions.innerHTML = "";

      data.top_predictions.forEach(item => {

        topPredictions.innerHTML += `

          <div class="prediction-row">

            <span>${item.food}</span>

            <span>${item.confidence}%</span>

          </div>
        `;
      });
    }
  }

  /* ---------- IMAGE UPLOAD ---------- */

  uploadForm.addEventListener(
    "submit",
    async (e) => {

      e.preventDefault();

      if (isProcessing) return;

      isProcessing = true;

      showLoading();

      try {

        const formData =
          new FormData(uploadForm);

        const file =
          fileInput.files[0];

        if (file && resultImage) {

          resultImage.src =
            URL.createObjectURL(file);

          resultImage.classList.remove(
            "hidden"
          );
        }

        const res = await fetch(
          "/analyze/do/",
          {
            method: "POST",

            headers: {
              "X-CSRFToken":
                getCSRFToken(),
            },

            body: formData,
          }
        );

        const data =
          await res.json();

        showResult(data);

      } catch (err) {

        console.error(err);

        showError(
          "Upload failed."
        );

      } finally {

        isProcessing = false;
      }
    }
  );

  /* ---------- IMAGE PREVIEW ---------- */

  if (fileInput) {

    fileInput.addEventListener(
      "change",
      () => {

        const file =
          fileInput.files[0];

        if (!file) {

          if (preview) {
            preview.classList.add(
              "hidden"
            );
          }

          return;
        }

        const reader =
          new FileReader();

        reader.onload = (e) => {

          if (preview) {

            preview.src =
              e.target.result;

            preview.classList.remove(
              "hidden"
            );
          }
        };

        reader.readAsDataURL(file);
      }
    );
  }

  /* ---------- CAMERA OPEN ---------- */

  if (cameraBtn) {

    cameraBtn.addEventListener(
      "click",
      async () => {

        try {

          stopCamera();

          stream =
            await navigator.mediaDevices.getUserMedia(
              {
                video: {
                  facingMode:
                    "environment",
                },
              }
            );

          video.srcObject =
            stream;

          video.classList.remove(
            "hidden"
          );

          captureBtn.classList.remove(
            "hidden"
          );

        } catch (err) {

          console.error(err);

          alert(
            "Camera not accessible"
          );
        }
      }
    );
  }

  /* ---------- CAMERA CAPTURE ---------- */

  if (captureBtn) {

    captureBtn.addEventListener(
      "click",
      () => {

        if (isProcessing)
          return;

        isProcessing = true;

        captureBtn.disabled = true;

        const ctx =
          canvas.getContext("2d");

        canvas.width = 224;

        canvas.height = 224;

        ctx.drawImage(
          video,
          0,
          0,
          224,
          224
        );

        canvas.toBlob(
          async (blob) => {

            if (!blob) {

              showError(
                "Capture failed"
              );

              resetCamera();

              return;
            }

            if (resultImage) {

              resultImage.src =
                URL.createObjectURL(
                  blob
                );

              resultImage.classList.remove(
                "hidden"
              );
            }

            showLoading();

            try {

              const formData =
                new FormData();

              formData.append(
                "file",
                blob,
                "camera.jpg"
              );

              const res =
                await fetch(
                  "/analyze/do/",
                  {
                    method:
                      "POST",

                    headers: {
                      "X-CSRFToken":
                        getCSRFToken(),
                    },

                    body:
                      formData,
                  }
                );

              const data =
                await res.json();

              showResult(data);

            } catch (err) {

              console.error(
                err
              );

              showError(
                "Camera failed."
              );
            }

            stopCamera();

            resetCamera();

          },
          "image/jpeg"
        );
      }
    );
  }

  /* ---------- STOP CAMERA ---------- */

  function stopCamera() {

    if (stream) {

      stream
        .getTracks()
        .forEach(track =>
          track.stop()
        );

      stream = null;
    }
  }

  /* ---------- RESET CAMERA ---------- */

  function resetCamera() {

    if (video) {
      video.classList.add(
        "hidden"
      );
    }

    if (captureBtn) {

      captureBtn.classList.add(
        "hidden"
      );

      captureBtn.disabled = false;
    }

    isProcessing = false;
  }

  /* ---------- MANUAL ENTRY ---------- */

  if (manualForm) {

    manualForm.addEventListener(
      "submit",
      (e) => {

        e.preventDefault();

        const food =
          document.getElementById(
            "foodName"
          ).value;

        const qty =
          parseFloat(
            document.getElementById(
              "foodQty"
            ).value
          );

        const calories =
          qty * 1.5;

        manualText.innerHTML = `

          <strong>Food:</strong> ${food}<br>

          <strong>Quantity:</strong> ${qty} g<br>

          <strong>Estimated Calories:</strong>
          ${Math.round(calories)} kcal
        `;

        manualResult.classList.remove(
          "hidden"
        );
      }
    );
  }
});

/* ---------- PROFILE DROPDOWN ---------- */

function toggleDropdown() {

  const menu =
    document.getElementById(
      "dropdownMenu"
    );

  if (menu) {
    menu.classList.toggle(
      "show"
    );
  }
}

window.addEventListener(
  "click",
  function (e) {

    const dropdown =
      document.querySelector(
        ".profile-dropdown"
      );

    if (
      dropdown &&
      !dropdown.contains(
        e.target
      )
    ) {

      const menu =
        document.getElementById(
          "dropdownMenu"
        );

      if (menu) {
        menu.classList.remove(
          "show"
        );
      }
    }
  }
);

const profileBtn =
  document.getElementById(
    "profileBtn"
  );

const dropdownMenu =
  document.getElementById(
    "dropdownMenu"
  );

if (profileBtn) {

  profileBtn.addEventListener(
    "click",
    function (e) {

      e.stopPropagation();

      if (dropdownMenu) {

        dropdownMenu.classList.toggle(
          "show"
        );
      }
    }
  );
}

document.addEventListener(
  "click",
  function () {

    if (dropdownMenu) {

      dropdownMenu.classList.remove(
        "show"
      );
    }
  }
);