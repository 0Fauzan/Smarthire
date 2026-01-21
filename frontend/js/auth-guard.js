// ===============================
// AUTH-GUARD.JS – STABLE VERSION
// ===============================

document.addEventListener("DOMContentLoaded", () => {

  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const role = localStorage.getItem("userRole");

  const currentPage = window.location.pathname.split("/").pop();

  // Public pages
  const publicPages = ["index.html", "login.html", "signup.html", ""];

  if (publicPages.includes(currentPage)) return;

  // Not logged in
  if (isLoggedIn !== "true" || !role) {
    console.warn("AuthGuard: Not logged in");
    window.location.replace("login.html");
    return;
  }

  // Role protection
  if (currentPage === "candidate-dashboard.html" && role !== "candidate") {
    window.location.replace("login.html");
    return;
  }

  if (currentPage === "hr-dashboard.html" && role !== "hr") {
    window.location.replace("login.html");
    return;
  }

  console.log("AuthGuard: Access granted");
});
