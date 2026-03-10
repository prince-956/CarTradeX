function showTab(tab) {

    document.querySelectorAll(".tab-content")
        .forEach(t => t.classList.remove("active"));

    document.querySelectorAll(".tab-btn")
        .forEach(b => b.classList.remove("active"));

    document.getElementById(tab).classList.add("active");

    event.target.classList.add("active");
}
