document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("smarthire_token");
  if (!token) return;

  try {
      const res = await fetch('http://127.0.0.1:5000/api/profile', {
          headers: { 'Authorization': `Bearer ${token}` }
      });
      const profile = await res.json();
      
      // Pre-fill form if on edit page
      if (document.getElementById("profileForm")) {
          const user = JSON.parse(localStorage.getItem("user") || "{}");
          document.getElementById("fullName").value = user.name || "";
          document.getElementById("role").value = profile.role || "";
          document.getElementById("education").value = profile.education || "";
          document.getElementById("skills").value = profile.skills || "";
          document.getElementById("projects").value = profile.projects || "";
      }
      
      // Populate view page
      if (document.getElementById("viewName")) {
          const user = JSON.parse(localStorage.getItem("user") || "{}");
          document.getElementById("viewName").innerText = user.name || "Candidate";
          document.getElementById("viewRole").innerText = profile.role || "Role not set";
          document.getElementById("viewEducation").innerText = profile.education || "Not set";
          document.getElementById("viewSkills").innerText = profile.skills || "Not set";
          document.getElementById("viewProjects").innerText = profile.projects || "Not set";
      }

  } catch(e) { console.error("Profile fetch error:", e); }

  // Save to Backend
  document.getElementById("profileForm")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const updated = {
          role: document.getElementById("role").value,
          education: document.getElementById("education").value,
          skills: document.getElementById("skills").value,
          projects: document.getElementById("projects").value
      };

      const res = await fetch('http://127.0.0.1:5000/api/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify(updated)
      });
      
      if (res.ok) {
          alert("Profile Saved to Database!");
          window.location.href = "profile.html";
      } else {
          alert("Failed to save profile.");
      }
  });
});