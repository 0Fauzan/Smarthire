// ===============================
// TECHNICAL INTERVIEW LOGIC
// ===============================

// Read selected language from URL
const params = new URLSearchParams(window.location.search);
const selectedLang = params.get("lang") || "c";

// DOM elements
const questionText = document.getElementById("questionText");
const optionsBox = document.getElementById("optionsBox");
const nextBtn = document.getElementById("nextBtn");

// Question index
let currentQuestion = 0;

// ===============================
// QUESTION BANK (TEMP / STATIC)
// ===============================
const QUESTIONS = {
  c: [
    {
      q: "Which of the following is a valid C data type?",
      options: ["string", "integer", "float", "character"],
      answer: "float"
    },
    {
      q: "What is the output of sizeof(int) in C?",
      options: ["2 bytes", "4 bytes", "8 bytes", "Depends on compiler"],
      answer: "Depends on compiler"
    }
  ],

  python: [
    {
      q: "Which keyword is used to define a function in Python?",
      options: ["func", "define", "def", "lambda"],
      answer: "def"
    },
    {
      q: "What is the output of print(type([]))?",
      options: ["list", "<class 'list'>", "array", "tuple"],
      answer: "<class 'list'>"
    }
  ],

  java: [
    {
      q: "Which keyword is used for inheritance in Java?",
      options: ["this", "extends", "implements", "super"],
      answer: "extends"
    },
    {
      q: "Which method is the entry point of a Java program?",
      options: ["start()", "main()", "run()", "init()"],
      answer: "main()"
    }
  ],

  javascript: [
    {
      q: "Which keyword declares a constant in JavaScript?",
      options: ["let", "var", "const", "static"],
      answer: "const"
    },
    {
      q: "What does typeof null return?",
      options: ["null", "object", "undefined", "number"],
      answer: "object"
    }
  ]
};

// Active question set
const activeQuestions = QUESTIONS[selectedLang];

// ===============================
// RENDER QUESTION
// ===============================
function renderQuestion() {
  const q = activeQuestions[currentQuestion];

  questionText.innerText = q.q;
  optionsBox.innerHTML = "";

  q.options.forEach(option => {
    const label = document.createElement("label");
    label.innerHTML = `
      <input type="radio" name="option" value="${option}">
      ${option}
    `;
    optionsBox.appendChild(label);
  });

  // Button text change on last question
  if (currentQuestion === activeQuestions.length - 1) {
    nextBtn.innerText = "Finish";
  } else {
    nextBtn.innerText = "Next";
  }
}

// ===============================
// NEXT BUTTON HANDLER
// ===============================
nextBtn.addEventListener("click", () => {
  const selected = document.querySelector('input[name="option"]:checked');

  if (!selected) {
    alert("Please select an answer");
    return;
  }

  currentQuestion++;

  if (currentQuestion < activeQuestions.length) {
    renderQuestion();
  } else {
    showCompletion();
  }
});

// ===============================
// COMPLETION SCREEN
// ===============================
function showCompletion() {
  questionText.innerText = "Interview Completed 🎉";
  optionsBox.innerHTML = `
    <p style="font-size:14px; opacity:0.8;">
      You have completed the technical interview for
      <b>${selectedLang.toUpperCase()}</b>.
    </p>
  `;
  nextBtn.style.display = "none";
}

// ===============================
// INIT
// ===============================
renderQuestion();