const basePrices = {
  "Swift VXI": 650000,
  "Baleno Alpha": 850000,
  "i20 Sportz": 800000,
  "Creta SX": 1500000,
  "City VX": 1400000,
  "Amaze S": 750000,
  "Nexon XM": 1100000,
  "Harrier XZ": 1900000,
  "Innova Crysta": 2300000,
  "Fortuner": 3800000,
  "XUV700 AX5": 2100000,
  "Thar LX": 1700000,
  "Slavia Style": 1600000,
  "Kushaq": 1500000,
  "Seltos HTX": 1700000,
  "Sonet GTX": 1300000,
  "Polo GT": 1100000,
  "Virtus": 1700000,
  "Kiger RXZ": 900000,
  "Triber": 750000
};


if (document.getElementById("sellCarModal")) {

let currentStep = 1;

document.addEventListener("DOMContentLoaded", function () {
  setupFileUpload();
  const mobileInput = document.getElementById("mobileNumber");
  if (mobileInput) {
    mobileInput.addEventListener("input", function () {
    this.value = this.value.replace(/\D/g, "").slice(0, 10);
  });

  const plateInput = document.querySelector("input[name='number_plate']");

  if (plateInput) {
    plateInput.addEventListener("input", function () {
      this.value = this.value.toUpperCase();
    });
  }

  document.getElementById("kmsDriven")?.addEventListener("input", calculateEstimatedPrice);
document.getElementById("regYear")?.addEventListener("change", calculateEstimatedPrice);
document.getElementById("fuelType")?.addEventListener("change", calculateEstimatedPrice);
document.getElementById("carModel")?.addEventListener("change", calculateEstimatedPrice);
document.getElementById("transmission")?.addEventListener("change", calculateEstimatedPrice);
document.getElementById("owners")?.addEventListener("change", calculateEstimatedPrice);

}

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

    document.querySelector(`[data-step="${step}"]`)
      .classList.add("active");

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
      showAlert("Please fill car details", "error");
      return false;
    }
  }

  if (step === 3) {

    const kms = document.getElementById("kmsDriven").value;
    const owners = document.getElementById("owners").value;
    const price = document.getElementById("expectedPrice").value;
    const images = document.getElementById("carImages").files;

    if (!kms || !owners || !price) {
      showAlert("Please fill all vehicle details", "error");
      return false;
    }

    if (images.length === 0) {
      showAlert("Please upload at least one car image", "error");
      return false;
    }

    if (price < 10000) {
      showAlert("Price must be at least ₹10,000", "error");
      return false;
    }

  }

  return true;
}

function submitForm() {
  if (!validateStep(3)) return;

  const formData = new FormData();

  new FormData(ownerForm).forEach((v, k) => formData.append(k, v));
  new FormData(carDetailsForm).forEach((v, k) => formData.append(k, v));
  new FormData(finalDetailsForm).forEach((v, k) => formData.append(k, v));

  fetch("/sell-car", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const modal = bootstrap.Modal.getInstance(
          document.getElementById("sellCarModal")
        );
        if (modal) modal.hide();
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

document.getElementById("sellCarModal")
  .addEventListener("hidden.bs.modal", function () {
    resetForm();
  });

}

function calculateEstimatedPrice() {

  const year = parseInt(document.getElementById("regYear").value);
  const kms = parseInt(document.getElementById("kmsDriven").value);
  const fuel = document.getElementById("fuelType").value;
  const model = document.getElementById("carModel").value;
  const transmission = document.getElementById("transmission").value;
  const owners = document.getElementById("owners").value;

  if (!year || !kms || !model) return;

  const basePrice = basePrices[model];
  if (!basePrice) return;

  const currentYear = new Date().getFullYear();
  const age = currentYear - year;

  let price = basePrice;

  // -------- AGE DEPRECIATION --------
  let depreciationRate = age <= 5
      ? 0.15 * age
      : (0.15 * 5) + (0.10 * (age - 5));

  let depreciation = basePrice * depreciationRate;

  // -------- KMS IMPACT --------
  let kmsFactor = (kms / 10000) * 0.02 * basePrice;

  // -------- FUEL ADJUSTMENT --------
  let fuelAdjust = 0;
  if (fuel === "DIESEL") fuelAdjust = basePrice * 0.05;
  if (fuel === "ELECTRIC") fuelAdjust = basePrice * 0.08;

  // -------- TRANSMISSION --------
  let transAdjust = 0;
  if (transmission === "AUTOMATIC") transAdjust = basePrice * 0.04;

  // -------- OWNER PENALTY --------
  let ownerPenalty = 0;

  if (owners == "1") ownerPenalty = basePrice * 0.05;
  if (owners == "2") ownerPenalty = basePrice * 0.10;
  if (owners == "3+") ownerPenalty = basePrice * 0.15;

  // -------- FINAL PRICE --------
  let estimated =
      price
      - depreciation
      - kmsFactor
      + fuelAdjust
      + transAdjust
      - ownerPenalty;

  if (estimated < 50000) estimated = 50000;

  let min = estimated * 0.95;
  let max = estimated * 1.05;

  document.getElementById("estimatedPrice").innerText =
      Math.round(estimated).toLocaleString("en-IN");

  document.getElementById("priceMin").innerText =
      Math.round(min).toLocaleString("en-IN");

  document.getElementById("priceMax").innerText =
      Math.round(max).toLocaleString("en-IN");

  document.getElementById("priceSuggestion").style.display = "block";
}
