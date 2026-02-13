if (document.getElementById("sellCarModal")) {

let currentStep = 1;

document.addEventListener("DOMContentLoaded", function () {
  setupFileUpload();
});

function handleSellCarClick() {
  const modal = new bootstrap.Modal(document.getElementById("sellCarModal"));
  modal.show();
}

function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const icon = input.nextElementSibling.querySelector("i");

  if (input.type === "password") {
    input.type = "text";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  } else {
    input.type = "password";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  }
}

function redirectToFullLogin() {
  window.location.href = "login.html";
}

function showAlert(message, type) {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type === "error" ? "danger" : "success"} alert-dismissible fade show position-fixed`;
  alertDiv.style.cssText =
    "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  document.body.appendChild(alertDiv);

  setTimeout(() => alertDiv.remove(), 5000);
}

function nextStep(step) {
  if (!validateStep(currentStep)) return;

  const current = document.getElementById("step" + currentStep);
  current.classList.add("slide-out-left");

  setTimeout(() => {
    current.style.display = "none";
    current.classList.remove("slide-out-left");

    document.querySelector(`[data-step="${currentStep}"]`)
      .classList.replace("active", "completed");

    const next = document.getElementById("step" + step);
    next.style.display = "block";
    next.classList.add("slide-in-right");

    document.querySelector(`[data-step="${step}"]`).classList.add("active");

    setTimeout(() => next.classList.remove("slide-in-right"), 400);
    currentStep = step;
  }, 300);
}

function prevStep(step) {
  const current = document.getElementById("step" + currentStep);
  current.classList.add("slide-out-left");

  setTimeout(() => {
    current.style.display = "none";
    current.classList.remove("slide-out-left");

    document.querySelector(`[data-step="${currentStep}"]`).classList.remove("active");

    const prev = document.getElementById("step" + step);
    prev.style.display = "block";
    prev.classList.add("slide-in-right");

    const p = document.querySelector(`[data-step="${step}"]`);
    p.classList.add("active");
    p.classList.remove("completed");

    setTimeout(() => prev.classList.remove("slide-in-right"), 400);
    currentStep = step;
  }, 300);
}

function validateStep(step) {
  if (step === 1) {
    const name = ownerName.value.trim();
    const mobile = mobileNumber.value.trim();
    const city = document.getElementById("city").value;

    if (!name || !mobile || !city) {
      showAlert("Please fill all required fields", "error");
      return false;
    }

    if (!/^\d{10}$/.test(mobile)) {
      showAlert("Invalid mobile number", "error");
      return false;
    }
  }

  if (step === 2) {
    if (!carBrand.value || !carModel.value || !regYear.value || !fuelType.value || !transmission.value) {
      showAlert("Fill car details", "error");
      return false;
    }
  }

  return true;
}

function submitForm() {
  const formData = new FormData();

  new FormData(ownerForm).forEach((v, k) => formData.append(k, v));
  new FormData(carDetailsForm).forEach((v, k) => formData.append(k, v));
  new FormData(finalDetailsForm).forEach((v, k) => formData.append(k, v));

  fetch("/sell-car", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        bootstrap.Modal.getInstance(sellCarModal).hide();
        successOverlay.style.display = "block";
      } else showAlert(data.error, "error");
    })
    .catch(() => showAlert("Server error", "error"));
}

function resetForm() {
  ownerForm.reset();
  carDetailsForm.reset();
  finalDetailsForm.reset();

  currentStep = 1;
  document.querySelectorAll(".step-content").forEach(s => s.style.display = "none");
  step1.style.display = "block";

  document.querySelectorAll(".progress-step").forEach(s => s.classList.remove("active", "completed"));
  document.querySelector('[data-step="1"]').classList.add("active");

  imagePreview.innerHTML = "";
}

function setupFileUpload() {
  const carImages = document.getElementById("carImages");
  if (!carImages) return;

  carImages.addEventListener("change", e => {
    const preview = imagePreview;
    preview.innerHTML = "";

    [...e.target.files].forEach(file => {
      if (!file.type.startsWith("image")) return;
      const reader = new FileReader();
      reader.onload = e => {
        const img = document.createElement("img");
        img.src = e.target.result;
        img.style.width = "100px";
        img.style.margin = "5px";
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  });
}
}

