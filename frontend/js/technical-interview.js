// ===============================
// TECHNICAL INTERVIEW – FINAL VERSION
// ===============================

document.addEventListener("DOMContentLoaded", () => {

  // -------------------------------
  // DOM ELEMENTS
  // -------------------------------
  const questionText = document.getElementById("questionText");
  const optionsBox = document.getElementById("optionsBox");
  const nextBtn = document.getElementById("nextBtn");
  const timerEl = document.getElementById("timer");

  // -------------------------------
  // LANGUAGE SELECTION
  // -------------------------------
  const params = new URLSearchParams(window.location.search);
  const selectedLanguage = params.get("lang") || "c";

  console.log("Technical Interview Language:", selectedLanguage);

  // -------------------------------
  // STATE
  // -------------------------------
  let currentIndex = 0;
  let selectedAnswer = null;
  let timer = null;
  let timeLeft = 60;

  let correctAnswers = 0;
  let answerLog = [];
  let timeTakenLog = [];

  // -------------------------------
  // QUESTION BANK (SAMPLE – EXPANDABLE)
  // -------------------------------
  const questions = [
    {
      question: "What is the time complexity of binary search?",
      options: ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
      answer: "O(log n)"
    },
    {
      question: "Which data structure follows FIFO?",
      options: ["Stack", "Queue", "Tree", "Graph"],
      answer: "Queue"
    },
    {
      question: "Which keyword is used to define a constant in C?",
      options: ["static", "final", "const", "define"],
      answer: "const"
    }
  ];

  // -------------------------------
  // TIMER FUNCTIONS
  // -------------------------------
  function startTimer() {
    clearInterval(timer);
    timeLeft = 60;
    updateTimerUI();

    timer = setInterval(() => {
      timeLeft--;
      updateTimerUI();

      if (timeLeft <= 0) {
        clearInterval(timer);
        autoNext();
      }
    }, 1000);
  }

  function updateTimerUI() {
    if (timerEl) {
      timerEl.innerText = `⏱️ Time left: ${timeLeft}s`;
    }
  }

  // -------------------------------
  // LOAD QUESTION
  // -------------------------------
  function loadQuestion() {
    selectedAnswer = null;
    optionsBox.innerHTML = "";

    const q = questions[currentIndex];
    questionText.innerText = q.question;

    q.options.forEach(option => {
      const label = document.createElement("label");
      label.innerHTML = `
        <input type="radio" name="option" value="${option}">
        ${option}
      `;
      label.addEventListener("click", () => {
        selectedAnswer = option;
      });
      optionsBox.appendChild(label);
    });

    startTimer();
  }

  // -------------------------------
  // ANSWER CHECK
  // -------------------------------
  function checkAnswer() {
    const q = questions[currentIndex];
    const isCorrect = selectedAnswer === q.answer;

    answerLog.push({
      question: q.question,
      selected: selectedAnswer,
      correct: q.answer,
      isCorrect: isCorrect
    });

    timeTakenLog.push(60 - timeLeft);

    if (isCorrect) {
      correctAnswers++;
    }
  }

  // -------------------------------
  // AUTO NEXT (TIMEOUT)
  // -------------------------------
  function autoNext() {
    checkAnswer();
    currentIndex++;

    if (currentIndex >= questions.length) {
      showCompletion();
    } else {
      loadQuestion();
    }
  }

  // -------------------------------
  // MANUAL NEXT
  // -------------------------------
  nextBtn.addEventListener("click", () => {
    if (!selectedAnswer) {
      alert("Please select an option");
      return;
    }

    clearInterval(timer);
    checkAnswer();
    currentIndex++;

    if (currentIndex >= questions.length) {
      showCompletion();
    } else {
      loadQuestion();
    }
  });

  // -------------------------------
  // AI SCORING LOGIC
  // -------------------------------
  function generateAIScore() {
    const total = questions.length;
    const accuracy = Math.round((correctAnswers / total) * 100);

    const avgTime = Math.round(
      timeTakenLog.reduce((a, b) => a + b, 0) / timeTakenLog.length
    );

    let rating = "Needs Improvement";
    let feedback = [];

    if (accuracy >= 80) {
      rating = "Excellent";
      feedback.push("Strong technical fundamentals");
    } else if (accuracy >= 50) {
      rating = "Good";
      feedback.push("Concepts are mostly clear");
    } else {
      feedback.push("Revise core technical topics");
    }

    if (avgTime <= 30) {
      feedback.push("Good time management");
    } else {
      feedback.push("Improve speed and confidence");
    }

    return {
      accuracy,
      avgTime,
      rating,
      feedback
    };
  }

  // -------------------------------
  // COMPLETION STATE
  // -------------------------------
  function showCompletion() {
    clearInterval(timer);

    const aiResult = generateAIScore();

    // SAVE FOR INSIGHTS PAGE
    localStorage.setItem("interviewSummary", JSON.stringify({
      type: "Technical Interview",
      language: selectedLanguage.toUpperCase(),
      date: new Date().toLocaleDateString(),
      totalQuestions: questions.length,
      correct: correctAnswers,
      accuracy: aiResult.accuracy,
      avgTime: aiResult.avgTime,
      rating: aiResult.rating,
      feedback: aiResult.feedback,
      answers: answerLog
    }));

    // UI UPDATE
    questionText.innerHTML = `
      <strong>Interview Completed 🎉</strong><br><br>
      <b>Language:</b> ${selectedLanguage.toUpperCase()}<br>
      <b>Accuracy:</b> ${aiResult.accuracy}%<br>
      <b>Average Time:</b> ${aiResult.avgTime}s<br>
      <b>Rating:</b> ${aiResult.rating}<br><br>
      <b>AI Feedback:</b><br>
      • ${aiResult.feedback.join("<br>• ")}
    `;

    optionsBox.innerHTML = "";
    if (timerEl) timerEl.innerText = "⏱️ Completed";

    nextBtn.innerText = "View Insights";
    nextBtn.onclick = () => {
      window.location.href = "candidate-insights.html";
    };
  }

  // -------------------------------
  // INIT
  // -------------------------------
  loadQuestion();

});