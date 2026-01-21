// ===============================
// CANDIDATE.JS – DASHBOARD LOGIC (STABLE + BACKEND)
// ===============================

document.addEventListener("DOMContentLoaded", () => {

  const resumeCard = document.getElementById("resumeCard");
  const resumeInput = document.getElementById("resumeInput");
  const resumeStatus = document.getElementById("resumeStatus");
  const logoutBtn = document.getElementById("logoutBtn");

  const API_BASE = "http://127.0.0.1:5000/candidate";

  let isUploading = false; // ✅ upload lock

  // -------------------------------
  // RESTORE RESUME STATE (FRONTEND)
  // -------------------------------
  const resumeUploaded = localStorage.getItem("resumeUploaded");
  const resumeName = localStorage.getItem("resumeName");

  if (resumeUploaded === "true" && resumeStatus) {
    resumeStatus.innerText = resumeName
      ? `Uploaded ✔ (${resumeName})`
      : "Uploaded ✔";
  }

  // -------------------------------
  // CLICK CARD → FILE PICKER
  // -------------------------------
  resumeCard?.addEventListener("click", () => {
    if (!isUploading) {
      resumeInput?.click();
    }
  });

  // -------------------------------
  // HANDLE FILE SELECTION + UPLOAD
  // -------------------------------
  resumeInput?.addEventListener("change", async () => {
    if (!resumeInput.files || resumeInput.files.length === 0) return;
    if (isUploading) return; // ✅ prevent double upload

    const file = resumeInput.files[0];

    // ✅ Frontend validation (SAFE)
    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ];

    if (!allowedTypes.includes(file.type)) {
      alert("Only PDF or DOCX files are allowed");
      resumeInput.value = "";
      return;
    }

    const user = JSON.parse(localStorage.getItem("user") || "{}");

    if (!user.email) {
      alert("User email not found. Please login again.");
      return;
    }

    isUploading = true;
    resumeStatus.innerText = "Uploading… ⏳";

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("email", user.email);

    try {
      const res = await fetch(`${API_BASE}/upload-resume`, {
        method: "POST",
        body: formData
      });

      const data = await res.json();

      if (!res.ok) {
        resumeStatus.innerText = "Upload failed ❌";
        alert(data.error || "Resume upload failed");
        isUploading = false;
        return;
      }

      // ✅ SUCCESS
      localStorage.setItem("resumeUploaded", "true");
      localStorage.setItem("resumeName", file.name);

      resumeStatus.innerText = `Uploaded ✔ (${file.name})`;
      alert("Resume uploaded & parsed successfully 🎉");

    } catch (err) {
      console.error(err);
      resumeStatus.innerText = "Upload failed ❌";
      alert("Server error while uploading resume");
    } finally {
      isUploading = false;
      resumeInput.value = ""; // reset input safely
    }
  });



  // -------------------------------
  // LOGOUT
  // -------------------------------
  logoutBtn?.addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "login.html";
  });

});
