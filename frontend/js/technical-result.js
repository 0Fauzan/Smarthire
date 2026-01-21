document.addEventListener("DOMContentLoaded", () => {
  const data = JSON.parse(sessionStorage.getItem("techResult"));

  if (!data) return;

  const score = Math.round((data.correct / data.total) * 100);

  document.getElementById("scoreText").innerText = score + "%";
  document.getElementById("correctText").innerText = data.correct;
  document.getElementById("wrongText").innerText = data.wrong;

  const minutes = Math.floor(data.time / 60);
  const seconds = data.time % 60;
  document.getElementById("timeText").innerText =
    `${minutes}m ${seconds}s`;
});