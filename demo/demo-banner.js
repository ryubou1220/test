document.addEventListener("DOMContentLoaded", () => {
  const banner = document.getElementById("demo-banner");
  const closeBtn = document.getElementById("demo-banner-close");

  if (closeBtn && banner) {
    closeBtn.addEventListener("click", () => {
      banner.classList.add("is-hidden");
    });
  }
});
