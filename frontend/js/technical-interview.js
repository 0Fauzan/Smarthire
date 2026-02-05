// ======================================================
// TECHNICAL-INTERVIEW.JS – FINAL STABLE VERSION
// ======================================================

document.addEventListener("DOMContentLoaded", () => {
  const questionText = document.getElementById("questionText");
  const optionsBox = document.getElementById("optionsBox");
  const editorContainer = document.getElementById("editorContainer");
  const nextBtn = document.getElementById("nextBtn");
  const timerEl = document.getElementById("timer");
  const langBadge = document.getElementById("languageBadge");
  const progressFill = document.getElementById("progressFill");

  // --- INTERVIEW STATE ---
  const params = new URLSearchParams(window.location.search);
  const companyParam = params.get("company");
  const langParam = params.get("lang");
  const selectedLanguage = (companyParam ? "python" : (langParam || "python")).toLowerCase();
  
  let currentIndex = 0;
  let selectedAnswer = null;
  let timerInterval = null;
  let timeLeft = 0;

  // --- QUESTION POOLS ---
  const langPool = {
    python: [{ type: "mcq", q: "Immutable data type?", o: ["List", "Tuple", "Set"], a: "Tuple" }, { type: "coding", q: "Write a function to return the nth Fibonacci number.", c: "def fibonacci(n):\n    # Write your code here\n    pass" }],
    java: [{ type: "mcq", q: "Keyword to prevent override?", o: ["static", "final", "abstract"], a: "final" }, { type: "coding", q: "Check if a string is a palindrome.", c: "public boolean isPalindrome(String s) {\n    // Code here\n}" }],
    javascript: [{ type: "mcq", q: "Output of 'typeof NaN'?", o: ["number", "string", "undefined"], a: "number" }, { type: "coding", q: "Write a function to deep-clone an object.", c: "function deepClone(obj) {\n    // Code here\n}" }],
    c: [{ type: "mcq", q: "Correct way to declare a pointer?", o: ["int p*;", "int *p;", "pointer p;"], a: "int *p;" }, { type: "coding", q: "Reverse a linked list.", c: "struct Node* reverse(struct Node* head) {\n    // Code here\n}" }],
    cpp: [{ type: "mcq", q: "Method implementation in subclass?", o: ["Overloading", "Overriding", "Abstraction"], a: "Overriding" }, { type: "coding", q: "Implement a Stack class.", c: "class Stack {\npublic:\n    // Code here\n};" }],
    sql: [{ type: "mcq", q: "Clause to filter aggregate functions?", o: ["WHERE", "HAVING", "GROUP BY"], a: "HAVING" }, { type: "coding", q: "Find second highest salary.", c: "-- SQL Query here\nSELECT..." }]
  };

  // Assign questions based on logic
  let questions = (langPool[selectedLanguage] || langPool["python"]).map(item => ({
      type: item.type,
      question: item.q,
      options: item.o,
      correct: item.a,
      starterCode: item.c
  }));

  // --- ACE EDITOR ---
  let editor;
  if (editorContainer) {
    editor = ace.edit("editorContainer");
    editor.setTheme("ace/theme/monokai");
    const aceModeMap = { 'cpp': 'c_cpp', 'c': 'c_cpp', 'javascript': 'javascript', 'python': 'python', 'java': 'java', 'sql': 'sql' };
    editor.session.setMode(`ace/mode/${aceModeMap[selectedLanguage] || 'python'}`);
    editor.setFontSize(14);
    editor.setShowPrintMargin(false);
  }

  // --- DATA STORAGE ---
  const reviewData = {
    meta: { 
        type: companyParam ? "Company Prep" : "Technical Interview", 
        language: selectedLanguage, 
        date: new Date().toLocaleDateString() 
    },
    results: []
  };

  // --- ENGINE FUNCTIONS ---
  function startTimer() {
    clearInterval(timerInterval);
    timeLeft = questions[currentIndex].type === 'coding' ? 300 : 60;
    updateTimerUI();
    timerInterval = setInterval(() => {
      timeLeft--;
      updateTimerUI();
      if (timeLeft <= 0) { clearInterval(timerInterval); saveAndNext(); }
    }, 1000);
  }

  function updateTimerUI() {
    if (timerEl) {
      const mins = Math.floor(timeLeft / 60);
      const secs = timeLeft % 60;
      timerEl.innerText = `⏱️ ${mins}:${secs.toString().padStart(2, '0')}`;
    }
  }

  function loadQuestion() {
    selectedAnswer = null;
    const q = questions[currentIndex];
    
    // Update Badge
    if (langBadge) langBadge.innerText = (companyParam || selectedLanguage).toUpperCase() + " SESSION";
    questionText.innerText = q.question;

    // Update Progress
    if (progressFill) {
      const percent = ((currentIndex + 1) / questions.length) * 100;
      progressFill.style.width = percent + "%";
    }

    // Toggle View
    if (q.type === "mcq") {
      optionsBox.style.display = "grid";
      editorContainer.style.display = "none";
      optionsBox.innerHTML = "";
      q.options.forEach(option => {
        const label = document.createElement("label");
        label.className = "option-label";
        label.innerHTML = `<input type="radio" name="opt" value="${option}"> ${option}`;
        label.onclick = () => {
          selectedAnswer = option;
          document.querySelectorAll('.option-label').forEach(l => l.classList.remove('active'));
          label.classList.add('active');
        };
        optionsBox.appendChild(label);
      });
    } else {
      optionsBox.style.display = "none";
      editorContainer.style.display = "block";
      editor.setValue(q.starterCode, -1);
      editor.focus();
    }

    if (currentIndex === questions.length - 1) {
      nextBtn.innerHTML = `Finish Session <i class="fa-solid fa-check" style="margin-left:8px;"></i>`;
    }

    startTimer();
  }

  function saveAndNext() {
    const q = questions[currentIndex];
    let userResponse = q.type === 'mcq' ? selectedAnswer : editor.getValue();
    
    reviewData.results.push({
      question: q.question,
      type: q.type,
      correct: q.correct,
      user: userResponse || "No Answer",
      isCorrect: q.type === 'mcq' ? (userResponse === q.correct) : "Pending Review",
      timeTaken: (q.type === 'coding' ? 300 : 60) - timeLeft
    });

    currentIndex++;
    if (currentIndex >= questions.length) {
      finishInterview();
    } else {
      loadQuestion();
    }
  }

  // --- 🛑 THE CRITICAL FIX FOR THE HANGING BUTTON ---
  async function finishInterview() {
    clearInterval(timerInterval);
    const token = localStorage.getItem("smarthire_token");

    if (!token) {
        alert("Session expired. Please log in again.");
        window.location.href = "login.html";
        return;
    }

    nextBtn.innerText = "Saving...";
    nextBtn.disabled = true;

    const correctCount = reviewData.results.filter(r => r.isCorrect === true).length;
    const totalQuestions = reviewData.results.length;
    const finalScore = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;

    const payload = {
      type: reviewData.meta.type,
      language: reviewData.meta.language,
      score: finalScore,
      results: reviewData.results,
      date: reviewData.meta.date
    };

    try {
      console.log("Saving to backend...");
      const response = await fetch('http://127.0.0.1:5000/api/interview/save', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json', 
            'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        localStorage.setItem("interviewReview", JSON.stringify(reviewData));
        window.location.href = "interview-summary.html";
      } else {
        const err = await response.json();
        console.error("Server Error:", err);
        alert("Error: " + (err.msg || "Could not save session"));
        resetButton();
      }
    } catch (error) {
      console.error("Network Error:", error);
      alert("Network error: Is the Python server running?");
      resetButton();
    }
  }

  function resetButton() {
    nextBtn.innerText = "Try Again";
    nextBtn.disabled = false;
  }

  // --- LISTENERS ---
  nextBtn.addEventListener("click", () => {
    if (questions[currentIndex].type === 'mcq' && !selectedAnswer) {
      alert("Please select an answer.");
      return;
    }
    saveAndNext();
  });

  loadQuestion();
});