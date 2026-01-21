document.addEventListener("DOMContentLoaded", () => {

  const data = JSON.parse(localStorage.getItem("interviewSummary"));

  if (!data) return;

  document.getElementById("interviewType").innerText = data.type;

  document.getElementById("summaryText").innerText =
    `Date: ${data.date} • Duration: ${data.duration}`;

  document.getElementById("metrics").innerText =
    `Questions: ${data.totalQuestions}
Attempted: ${data.attempted}
Correct: ${data.correct}`;

  document.getElementById("statusText").innerText = data.status;

});