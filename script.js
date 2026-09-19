document.addEventListener("DOMContentLoaded", () => {
  const navToggle = document.getElementById("nav-toggle");
  const mainNav = document.getElementById("main-nav");

  if (navToggle && mainNav) {
    navToggle.addEventListener("click", () => {
      mainNav.classList.toggle("open");
    });

    mainNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mainNav.classList.remove("open");
      });
    });
  }

  const ctaForm = document.querySelector(".cta-form");
  if (ctaForm) {
    ctaForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const input = ctaForm.querySelector("input[type='email']");
      if (input && input.value) {
        alert(`${input.value} 宛にショップ開設のご案内をお送りします。`);
        input.value = "";
      }
    });
  }
});
