document.addEventListener("DOMContentLoaded", loadWishlist);

function loadWishlist() {
  fetch("/api/wishlist")
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById("wishlistContainer");
      const emptyState = document.getElementById("emptyWishlist");
      const countSpan = document.getElementById("wishlistCount");

      container.innerHTML = "";
      countSpan.textContent = data.cars.length;

    if (data.cars.length === 0) {
  emptyState.style.display = "block";
  container.innerHTML = ""; // clear old content
  return;
}


      emptyState.style.display = "none";

      data.cars.forEach(car => {
        const card = `
        <div class="wishlist-card">
          <div class="row align-items-center">
            <div class="col-md-4">
              <img src="/static/images/${car.image}" 
                   class="wishlist-img" alt="Car">
            </div>
            <div class="col-md-6">
              <h5>${car.year} ${car.brand} ${car.model}</h5>
              <p class="text-muted">${car.city}</p>
              <h6>₹${Number(car.price).toLocaleString()}</h6>
            </div>
            <div class="col-md-2 text-end">
              <a href="/car/${car.car_id}" 
                 class="btn btn-primary-custom mb-2">
                 View Details
              </a>
              <button class="btn btn-outline-danger"
                      onclick="removeFromWishlist(${car.car_id})">
                 Remove
              </button>
            </div>
          </div>
        </div>
        `;

        container.innerHTML += card;
      });
    });
}

// Remove from wishlist (DB-based)
function removeFromWishlist(carId) {
  fetch(`/remove_from_wishlist/${carId}`, { method: "POST" })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      loadWishlist();  // refresh page
    });
}