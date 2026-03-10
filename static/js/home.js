// Initialize AOS (Animate On Scroll)
AOS.init({
  duration: 800,
  once: true,
  offset: 100,
});

// Animated Counter for Stats
function animateCounter(element, target, duration) {
  let start = 0;
  const increment = target / (duration / 16);

  const timer = setInterval(() => {
    start += increment;
    element.textContent = Math.floor(start);

    if (start >= target) {
      element.textContent = target;
      clearInterval(timer);
    }
  }, 16);
}

// Initialize counters when stats section comes into view
const statsSection = document.querySelector(".stats-section");
let countersAnimated = false;

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting && !countersAnimated) {
      const counters = document.querySelectorAll("[data-count]");
      counters.forEach((counter) => {
        const target = parseInt(counter.getAttribute("data-count"));
        animateCounter(counter, target, 2000);
      });
      countersAnimated = true;
    }
  });
});

observer.observe(statsSection);

// Search functionality
function searchCars() {
  const brand = document.getElementById("brandSelect").value;
  const budget = document.getElementById("budgetSelect").value;
  const location = document.getElementById("locationSelect").value;

  // Build query parameters
  const params = new URLSearchParams();
  if (brand) params.append("brand", brand);
  if (budget) params.append("budget", budget);
  if (location) params.append("location", location);

  // Redirect to buy-cars page with search parameters
  window.location.href = `buy-cars.html?${params.toString()}`;
}

// Add loading animation for search
document.querySelector(".search-btn").addEventListener("click", function () {
  this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
  setTimeout(() => {
    searchCars();
  }, 500);
});

// Add hover effects to feature cards
document.querySelectorAll(".feature-card").forEach((card) => {
  card.addEventListener("mouseenter", function () {
    this.style.transform = "translateY(-8px) scale(1.02)";
  });

  card.addEventListener("mouseleave", function () {
    this.style.transform = "translateY(0) scale(1)";
  });
});

function searchCars() {

    let params = new URLSearchParams();

    document.querySelectorAll(".home-filter").forEach(el => {

        if (el.value) {

            // kms format for backend
            if (el.name === "kms") {
                params.append("kms", el.value + "B");
            } else {
                params.append(el.name, el.value);
            }

        }

    });

    window.location.href = "/buy?" + params.toString();
}
