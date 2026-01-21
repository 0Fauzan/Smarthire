// ===============================
// UI.JS – THEME + UI EFFECTS (FINAL)
// ===============================

document.addEventListener("DOMContentLoaded", () => {
  /* ===============================
     THEME TOGGLE (GLOBAL FIX)
  ================================ */
  const themeToggle = document.getElementById("themeToggle");

  const applyTheme = (theme) => {
    const icon = themeToggle?.querySelector("i");

    if (theme === "light") {
      document.body.classList.add("light");
      if (icon) {
        icon.classList.remove("fa-moon");
        icon.classList.add("fa-sun");
      }
    } else {
      document.body.classList.remove("light");
      if (icon) {
        icon.classList.remove("fa-sun");
        icon.classList.add("fa-moon");
      }
    }
  };

  // ✅ Load saved theme safely
  const savedTheme = localStorage.getItem("theme") || "dark";
  applyTheme(savedTheme);

  // ✅ Toggle theme on click
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const newTheme = document.body.classList.contains("light")
        ? "dark"
        : "light";

      localStorage.setItem("theme", newTheme);
      applyTheme(newTheme);
    });
  }

  /* ===============================
     FEATURE CARD REVEAL (HOME)
  ================================ */
  document.querySelectorAll(".reveal").forEach((card, index) => {
    setTimeout(() => {
      card.classList.add("show");
    }, index * 120);
  });
});
