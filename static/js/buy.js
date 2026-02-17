// // run only if buy page exists
// if (document.getElementById("cars-container")) {

//   // Initialize AOS
//   AOS.init({
//     duration: 800,
//     once: true,
//     offset: 100,
//   });

//   const filters = document.querySelectorAll(".filter");
//   let lastCheckedRadio = {}; // group-wise memory

//   filters.forEach(f => {

//     // CHECKBOX
//     if (f.type === "checkbox") {
//       f.addEventListener("change", applyFilters);
//     }

//     // RADIO (toggle behavior)
//     if (f.type === "radio") {
//       f.addEventListener("click", function () {
//         const group = this.name;

//         if (lastCheckedRadio[group] === this) {
//           this.checked = false;
//           lastCheckedRadio[group] = null;
//         } else {
//           lastCheckedRadio[group] = this;
//         }

//         applyFilters();
//       });
//     }
//   });

//   function applyFilters() {
//     let params = new URLSearchParams();

//     filters.forEach(f => {
//       if (f.checked && f.value !== "All") {
//         params.append(f.dataset.name, f.value);
//       }
//     });

//     fetch("/filter?" + params.toString())
//       .then(res => res.text())
//       .then(html => {
//         document.getElementById("cars-container").innerHTML = html;
//       });
//   }

// }
// if (document.getElementById("cars-container")) {

//   const filters = document.querySelectorAll(".filter");
//   const sortFilter = document.getElementById("sortFilter");

//   filters.forEach(f => {
//     f.addEventListener("change", applyFilters);
//   });

//   sortFilter.addEventListener("change", applyFilters);

//   function applyFilters() {
//     let params = new URLSearchParams();

//     filters.forEach(f => {
//       if (f.checked && f.value !== "All") {
//         params.append(f.dataset.name, f.value);
//       }
//     });

//     // Add sorting option
//     params.append("sort", sortFilter.value);

//     fetch("/filter?" + params.toString())
//       .then(res => res.text())
//       .then(html => {
//         document.getElementById("cars-container").innerHTML = html;
//       });
//   }
// }





// Run only if buy page exists
if (document.getElementById("cars-container")) {

    // Initialize animation
    AOS.init({
        duration: 800,
        once: true,
        offset: 100,
    });

    const filters = document.querySelectorAll(".filter");
    const sortFilter = document.getElementById("sortFilter");

    let lastCheckedRadio = {}; // radio toggle memory


    // -----------------------------
    // FILTER EVENTS
    // -----------------------------
    filters.forEach(f => {

        // Checkbox
        if (f.type === "checkbox") {
            f.addEventListener("change", applyFilters);
        }

        // Radio toggle support
        if (f.type === "radio") {
            f.addEventListener("click", function () {

                const group = this.name;

                if (lastCheckedRadio[group] === this) {
                    this.checked = false;
                    lastCheckedRadio[group] = null;
                } else {
                    lastCheckedRadio[group] = this;
                }

                applyFilters();
            });
        }
    });


    // Sort change
    if (sortFilter) {
        sortFilter.addEventListener("change", applyFilters);
    }


    // -----------------------------
    // APPLY FILTER FUNCTION
    // -----------------------------
    function applyFilters() {

        let params = new URLSearchParams();

        filters.forEach(f => {
            if (f.checked && f.value !== "All") {
                params.append(f.name, f.value);   // IMPORTANT FIX
            }
        });

        if (sortFilter) {
            params.append("sort", sortFilter.value);
        }

        fetch("/filter?" + params.toString())
            .then(res => res.text())
            .then(html => {

                document.getElementById("cars-container").innerHTML = html;

                updateCarCount();
            });
    }


    // -----------------------------
    // UPDATE CAR COUNT
    // -----------------------------
    function updateCarCount() {
        const count = document.querySelectorAll(".car-card").length;
        const counter = document.getElementById("carCount");

        if (counter) {
            counter.innerText = count;
        }
    }


    // Initial count on page load
    window.addEventListener("load", updateCarCount);

}
