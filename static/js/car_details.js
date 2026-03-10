document.addEventListener("DOMContentLoaded", function () {
  calculateEMI();
});

function calculateEMI() {
  const loanAmount = document.getElementById("loanAmount").value;
  const tenure = document.getElementById("tenure").value;
  const interestRate = 8.5; // 8.5% annual interest rate

  document.getElementById("loanAmountValue").textContent =
    `₹${(loanAmount / 100000).toFixed(1)}L`;
  document.getElementById("tenureValue").textContent = `${tenure} Years`;

  const monthlyRate = interestRate / (12 * 100);
  const months = tenure * 12;

  const emi =
    (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, months)) /
    (Math.pow(1 + monthlyRate, months) - 1);

  document.getElementById("emiAmount").textContent =
    `₹${Math.round(emi).toLocaleString()}`;
}

function showContactModal() {
  const modal = new bootstrap.Modal(document.getElementById("contactModal"));
  modal.show();
}

function scheduleTestDrive() {
  alert(
    "Test drive scheduling feature coming soon! Our team will contact you to arrange a convenient time."
  );
}

function scheduleCallback() {
  alert("Callback scheduled! Our team will call you within 2 hours.");
  const modal = bootstrap.Modal.getInstance(
    document.getElementById("contactModal")
  );
  modal.hide();
}


document.addEventListener("DOMContentLoaded", function () {
  const buyBtn = document.getElementById("buyBtn");

  if (!buyBtn) {
    console.log("❌ Buy button NOT found!");
    return;
  }

  buyBtn.addEventListener("click", function () {
    const carId = this.dataset.id;
    console.log("Redirecting to payment for car:", carId);

    fetch(`/buy_car/${carId}`, { method: "POST" })
      .then(res => res.json())
      .then(data => {
        console.log("Server response:", data);
        if (data.success && data.redirect) {
          window.location.href = data.redirect;
        } else if (data.redirect) {
          window.location.href = data.redirect;
        } else {
          alert(data.message || "Unable to proceed");
        }
      })
      .catch(err => console.error(err));
  });
});
