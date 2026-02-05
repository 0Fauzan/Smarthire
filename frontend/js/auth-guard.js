// ===============================================
// AUTH-GUARD.JS – STABLE VERSION (WITH LOGOUT)
// ===============================================

document.addEventListener("DOMContentLoaded", () => {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const role = localStorage.getItem("userRole");
  const currentPage = window.location.pathname.split("/").pop();

  // 1. PUBLIC PAGES ACCESS
  // Includes index, login, signup and the root path
  const publicPages = ["index.html", "login.html", "signup.html", "", "index.html"];
  if (publicPages.includes(currentPage)) return;

  // 2. SECURITY CHECK: If not logged in, kick to login
  if (isLoggedIn !== "true" || !role) {
      console.warn("AuthGuard: Unauthorized access attempt.");
      localStorage.clear(); // Clear any corrupted data
      window.location.replace("login.html");
      return;
  }

  // 3. ROLE PROTECTION: Prevent Candidates from entering HR areas and vice versa
  if (currentPage.startsWith("candidate-") && role !== "candidate") {
      window.location.replace("login.html");
      return;
  }

  if (currentPage.startsWith("hr-") && role !== "hr") {
      window.location.replace("login.html");
      return;
  }

  // 4. GLOBAL LOGOUT HANDLER
  // This attaches to any element with id="logoutBtn" on any page
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
      logoutBtn.addEventListener("click", (e) => {
          e.preventDefault();
          console.log("AuthGuard: Logging out user...");
          
          // Clear all session data
          localStorage.clear();
          sessionStorage.clear();
          
          // Redirect to login
          window.location.replace("login.html");
      });
  }

  console.log(`AuthGuard: Access granted for ${role} on ${currentPage}`);
});