document.addEventListener("DOMContentLoaded", function () {
  const ham = document.getElementById("ham-btn");
  const nav = document.getElementById("nav-links");

  ham.addEventListener("click", () => {
      nav.classList.toggle("show");
  });
});
