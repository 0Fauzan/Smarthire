// ===============================
// AUTH.JS – FINAL FIXED VERSION
// ===============================

const API_BASE = "http://127.0.0.1:5000/auth";

document.addEventListener("DOMContentLoaded", () => {

  /* ===============================
     SOCIAL LOGIN PLACEHOLDERS
  ================================ */
  document.querySelectorAll(".social-btn.google").forEach(btn => {
    btn.addEventListener("click", () => {
      alert("Google login will be available soon 🚀");
    });
  });

  document.querySelectorAll(".social-btn.github").forEach(btn => {
    btn.addEventListener("click", () => {
      alert("GitHub login will be available soon 🚀");
    });
  });

  /* ===============================
     SIGNUP FORM
  ================================ */
  const signupForm = document.getElementById("signupForm");

  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const payload = {
        name: document.getElementById("fullName").value.trim(),
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value,
        role: document.getElementById("role").value
      };

      if (!payload.name || !payload.email || !payload.password || !payload.role) {
        alert("Please fill all fields");
        return;
      }

      try {
        const res = await fetch(`${API_BASE}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
          alert(data.error || "Signup failed");
          return;
        }

        alert("Account created successfully 🎉");
        window.location.href = "login.html";

      } catch (err) {
        console.error(err);
        alert("Server error");
      }
    });
  }

  /* ===============================
     LOGIN FORM
  ================================ */
  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const payload = {
        email: document.getElementById("loginEmail").value.trim(),
        password: document.getElementById("loginPassword").value
      };

      try {
        const res = await fetch(`${API_BASE}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
          alert(data.error || "Login failed");
          return;
        }

        // ✅ STORE TOKEN & ROLE (MATCHES AUTH-GUARD)
        // LOGIN SUCCESS — DO NOT CHANGE ORDER
        localStorage.setItem("smarthire_token", "dev-session-token");
        localStorage.setItem("userRole", data.user.role);
        localStorage.setItem("isLoggedIn", "true");
        localStorage.setItem("user", JSON.stringify(data.user));

        console.log("LOGIN STORAGE SET", {
        token: localStorage.getItem("smarthire_token"),
        role: localStorage.getItem("userRole")
});

  if (data.user.role === "candidate") {
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("userRole", "candidate");
    window.location.assign("candidate-dashboard.html");
  }else if (data.user.role === "hr") {
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("userRole", "hr");
     window.location.assign("hr-dashboard.html");
}
 else {
        alert("Unknown user role"); 
      }

      } catch (err) {
        console.error(err);
        alert("Server error");
      }
    });
  }

});
