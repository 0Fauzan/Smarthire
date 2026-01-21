document.getElementById("resumeForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const userId = document.getElementById("user_id").value;

  const payload = {
    user_id: Number(userId),
    full_name: document.getElementById("full_name").value,
    role: document.getElementById("role").value,
    technical_skills: document.getElementById("skills").value.split(","),
    project_title: document.getElementById("project").value
  };

  const response = await fetch("http://127.0.0.1:5000/candidate/resume", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const result = await response.json();

  document.getElementById("status").innerText =
    result.message || "Resume submitted";

  // Move to interview page (next step)
  setTimeout(() => {
    window.location.href = `interview.html?user_id=${userId}`;
  }, 1000);
});

// ===============================
// ATS CARD TOGGLE (SINGLE SOURCE)
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const atsCard = document.getElementById("atsCard");
  if (!atsCard) return;

  atsCard.addEventListener("click", (e) => {
    if (e.target.closest("button")) return;
    atsCard.classList.toggle("expanded");
  });
    // 🔹 TEMP ATS DATA (will be replaced by backend later)
updateATS({
  score: 72,
  keywords: 78,
  formatting: 85,
  sections: 70,
  status: "Good Match"
});
});
// -------------------------------
// ATS UI UPDATE FUNCTION
// -------------------------------
function updateATS(data) {
  const atsValue = document.getElementById("atsValue");
  const atsMiniValue = document.getElementById("atsMiniValue");
  const kwScore = document.getElementById("kwScore");
  const fmtScore = document.getElementById("fmtScore");
  const secScore = document.getElementById("secScore");
  const atsStatus = document.getElementById("atsStatus");

  if (!atsValue) return; // safety check

  atsValue.innerText = data.score;
  if (atsMiniValue) atsMiniValue.innerText = data.score;

  if (kwScore) kwScore.innerText = data.keywords + "%";
  if (fmtScore) fmtScore.innerText = data.formatting + "%";
  if (secScore) secScore.innerText = data.sections + "%";

  if (atsStatus) atsStatus.innerText = data.status;
}
