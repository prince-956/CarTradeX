// Initialize page
document.addEventListener("DOMContentLoaded", function () {
  checkLoginStatus();
  loadCarListings();
  setupFilters();
});


function getStatusIcon(status) {
  const icons = {
    pending: "clock",
    approved: "check-circle",
    rejected: "exclamation-triangle",
    sold: "handshake",
  };
  return icons[status] || "question-circle";
}

function getStatusText(status) {
  const texts = {
    pending: "Under Review",
    approved: "Live",
    rejected: "Needs Attention",
    sold: "Sold",
  };
  return texts[status] || "Unknown";
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}