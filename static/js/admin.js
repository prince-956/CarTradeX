document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll(".content-section");
    const navLinks = document.querySelectorAll(".nav-link");

    function showSection(sectionId) {
        sections.forEach(sec => sec.style.display = "none");
        document.getElementById(sectionId).style.display = "block";

        navLinks.forEach(link => link.classList.remove("active"));
        document.querySelector(`[data-section="${sectionId.replace("-section","")}"]`)
            .classList.add("active");
    }

    navLinks.forEach(btn => {
        btn.addEventListener("click", function () {
            const section = this.getAttribute("data-section") + "-section";
            showSection(section);
        });
    });

    //default:show dashboard
    showSection("dashboard-section");
});

// Sidebar toggle for mobile
const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("sidebarToggle");
const overlay = document.getElementById("sidebarOverlay");

toggleBtn.addEventListener("click", function () {
    sidebar.classList.toggle("show");
    overlay.style.display = sidebar.classList.contains("show") ? "block" : "none";
});

// Close sidebar when clicking outside
overlay.addEventListener("click", function () {
    sidebar.classList.remove("show");
    overlay.style.display = "none";
});
