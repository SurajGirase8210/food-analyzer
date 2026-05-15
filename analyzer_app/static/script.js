console.log("Script loaded");

document.addEventListener("DOMContentLoaded", function () {
  /* ---------- ELEMENTS ---------- */
  const uploadForm = document.getElementById("uploadForm");
  
  const resultDiv = document.getElementById("result");

  const fileInput = document.querySelector('input[type="file"]');
  const preview = document.getElementById("preview");

  const cameraBtn = document.getElementById("cameraBtn");
  const video = document.getElementById("cameraPreview");
  const captureBtn = document.getElementById("captureBtn");
  const canvas = document.getElementById("cameraCanvas");

  const manualForm = document.getElementById("manualForm");
  const manualResult = document.getElementById("manualResult");
  const manualText = document.getElementById("manualText");

  let stream = null;
  let isProcessing = false;

  /* ---------- CSRF ---------- */
  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
  }

  /* ---------- UI HELPERS ---------- */

function showLoading(msg) {

  resultDiv.classList.remove("hidden");

  document.getElementById("foodTitle").innerText =
    "Analyzing...";

  document.getElementById("confidenceText").innerText =
    "...";

  document.getElementById("caloriesText").innerText =
    "...";

  document.getElementById("proteinText").innerText =
    "...";

  document.getElementById("fatText").innerText =
    "...";

  document.getElementById("carbsText").innerText =
    "...";
}

function showError(msg) {

  resultDiv.classList.remove("hidden");

  document.getElementById("foodTitle").innerText =
    "Error";

  document.getElementById("confidenceText").innerText =
    "0%";

  document.getElementById("caloriesText").innerText =
    msg;

  document.getElementById("proteinText").innerText =
    "-";

  document.getElementById("fatText").innerText =
    "-";

  document.getElementById("carbsText").innerText =
    "-";
}

function showResult(data) {

  resultDiv.classList.remove("hidden");

  if (data.error) {
    showError(data.error);
    return;
  }

  document.getElementById("foodTitle").innerText =
    data.food;

  document.getElementById("confidenceText").innerText =
    data.confidence + "%";

  document.getElementById("caloriesText").innerText =
    data.calories ?? "N/A";

  document.getElementById("proteinText").innerText =
    (data.protein ?? "N/A") + " g";

  document.getElementById("fatText").innerText =
    (data.fat ?? "N/A") + " g";

  document.getElementById("carbsText").innerText =
    (data.carbs ?? "N/A") + " g";
}

  /* ---------- IMAGE UPLOAD ---------- */
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (isProcessing) return;
    isProcessing = true;

    showLoading("Analyzing image...");

    try {
      const formData = new FormData(uploadForm);

      const file = fileInput.files[0];

if(file){
    document.getElementById("resultImage").src =
        URL.createObjectURL(file);
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
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (!file) {
      preview.classList.add("hidden");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
      preview.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
  });

  /* ---------- CAMERA OPEN ---------- */
  cameraBtn.addEventListener("click", async () => {
    try {
      stopCamera();

      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });

      video.srcObject = stream;

      video.classList.remove("hidden");
      captureBtn.classList.remove("hidden");
    } catch (err) {
      console.error(err);
      alert("Camera not accessible");
    }
  });

  /* ---------- CAMERA CAPTURE ---------- */
  captureBtn.addEventListener("click", () => {
    if (isProcessing) return;

    isProcessing = true;
    captureBtn.disabled = true;

    const ctx = canvas.getContext("2d");

    canvas.width = 224;
    canvas.height = 224;

    ctx.drawImage(video, 0, 0, 224, 224);

    canvas.toBlob(async (blob) => {
      document.getElementById("resultImage").src =
    URL.createObjectURL(blob);
      if (!blob) {
        showError("Capture failed");
        resetCamera();
        return;
      }

      showLoading("Analyzing captured image...");

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

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
  }

  function resetCamera() {
    video.classList.add("hidden");
    captureBtn.classList.add("hidden");
    captureBtn.disabled = false;
    isProcessing = false;
  }

  /* ---------- MANUAL ENTRY ---------- */
  manualForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const food = document.getElementById("foodName").value;
    const qty = parseFloat(document.getElementById("foodQty").value);

    const calories = qty * 1.5;

    manualText.innerHTML = `
      <strong>Food:</strong> ${food}<br>
      <strong>Quantity:</strong> ${qty} g<br>
      <strong>Estimated Calories:</strong> ${Math.round(calories)} kcal
    `;

    manualResult.classList.remove("hidden");
  });
});

function toggleDropdown() {
    const menu = document.getElementById("dropdownMenu");
    menu.classList.toggle("show");
}

/* Close dropdown when clicking outside */
window.addEventListener("click", function (e) {
    const dropdown = document.querySelector(".profile-dropdown");

    if (!dropdown.contains(e.target)) {
        const menu = document.getElementById("dropdownMenu");
        if (menu) menu.classList.remove("show");
    }
});

const profileBtn = document.getElementById("profileBtn");
const dropdownMenu = document.getElementById("dropdownMenu");

if (profileBtn) {
    profileBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        dropdownMenu.classList.toggle("show");
    });
}

/* Close when clicking outside */
document.addEventListener("click", function () {
    if (dropdownMenu) {
        dropdownMenu.classList.remove("show");
    }
});