document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("profileForm");
  const status = document.getElementById("saveStatus");

  // Restore saved profile
  const profile = JSON.parse(localStorage.getItem("candidateProfile") || "{}");

  Object.keys(profile).forEach(key => {
    const input = document.getElementById(key);
    if (input) input.value = profile[key];
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const data = {
      fullName: fullName.value,
      role: role.value,
      education: education.value,
      skills: skills.value,
      projects: projects.value
    };

    localStorage.setItem("candidateProfile", JSON.stringify(data));

    status.innerText = "Profile saved successfully ✔";
  });
});