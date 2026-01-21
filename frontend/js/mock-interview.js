// ===============================
// AI MOCK INTERVIEW – TIMER + EVALUATION
// ===============================

document.addEventListener("DOMContentLoaded", () => {

  const questionText = document.getElementById("questionText");
  const answerBox = document.querySelector("textarea");
  const timerEl = document.getElementById("timer");
  const nextBtn = document.getElementById("nextBtn");
  const qCounter = document.getElementById("qCounter");

  let currentIndex = 0;
  let timer = null;
  let timeLeft = 120; // 2 minutes per question
  let totalTime = 0;

  const responses = [];

  // -------------------------------
  // QUESTIONS (TEMP)
  // -------------------------------
  const questions = [
    "Tell me about yourself.",
    "Explain a challenging project you worked on.",
    "What are your strengths and weaknesses?",
    "Describe a situation where you solved a problem.",
    "Why should we hire you?"
  ];

  // -------------------------------
  // TIMER
  // -------------------------------
  function startTimer() {
    clearInterval(timer);
    timeLeft = 120;
    updateTimerUI();

    timer = setInterval(() => {
      timeLeft--;
      updateTimerUI();

      if (timeLeft <= 0) {
        clearInterval(timer);
        saveAnswerAndNext();
      }
    }, 1000);
  }

  function updateTimerUI() {
    timerEl.innerText = `⏱️ ${Math.floor(timeLeft / 60)
      .toString()
      .padStart(2, "0")}:${(timeLeft % 60).toString().padStart(2, "0")}`;
  }

  // -------------------------------
  // LOAD QUESTION
  // -------------------------------
  function loadQuestion() {
    answerBox.value = "";
    questionText.innerText = questions[currentIndex];
    qCounter.innerText = `(${currentIndex + 1} / ${questions.length})`;
    startTimer();
  }

  // -------------------------------
  // SAVE ANSWER
  // -------------------------------
  function saveAnswerAndNext() {
    clearInterval(timer);

    const answer = answerBox.value.trim();

    responses.push({
      question: questions[currentIndex],
      answer,
      timeTaken: 120 - timeLeft
    });

    totalTime += (120 - timeLeft);
    currentIndex++;

    if (currentIndex >= questions.length) {
      finishInterview();
    } else {
      loadQuestion();
    }
  }

  // -------------------------------
  // NEXT BUTTON
  // -------------------------------
  nextBtn.addEventListener("click", () => {
    if (!answerBox.value.trim()) {
      alert("Please enter your answer");
      return;
    }
    saveAnswerAndNext();
  });

  // -------------------------------
  // FINISH INTERVIEW
  // -------------------------------
  function finishInterview() {
    clearInterval(timer);

    sessionStorage.setItem("mockInterviewResult", JSON.stringify({
      totalQuestions: questions.length,
      totalTime,
      responses
    }));

    questionText.innerHTML = `
      <strong>Interview Completed 🎉</strong><br><br>
      Your responses have been recorded.<br>
      AI evaluation will be shown in Insights.
    `;

    answerBox.style.display = "none";
    timerEl.innerText = "⏱️ Completed";
    nextBtn.disabled = true;
    nextBtn.style.opacity = "0.6";
  }

  // -------------------------------
  // INIT
  // -------------------------------
  loadQuestion();

});