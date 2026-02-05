// ==========================================
// CANDIDATE-INSIGHTS.JS – DATA ANALYTICS
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
  // 1. ✅ LOAD DATA (Standardized Key)
  const review = JSON.parse(localStorage.getItem("interviewReview"));

  if (!review) {
      document.getElementById("summaryText").innerText = "No session data found. Complete an interview to see insights.";
      return;
  }

  const results = review.results;
  const total = results.length;
  const correct = results.filter(q => q.isCorrect === true).length;
  const codingTasks = results.filter(q => q.type === 'coding');

  // 2. ✅ CALCULATE ACCURACY
  const accuracyPercent = total > 0 ? Math.round((correct / total) * 100) : 0;
  document.getElementById("accuracyPercent").innerText = accuracyPercent + "%";
  document.getElementById("accuracyText").innerText = `Solved ${correct} out of ${total} challenges.`;

  // 3. ✅ CALCULATE SKILL PROFICIENCY (REAL LOGIC)
  
  // Logic & Reasoning = Accuracy on MCQs
  const mcqs = results.filter(r => r.type === 'mcq');
  const mcqCorrect = mcqs.filter(r => r.isCorrect).length;
  const logicScore = mcqs.length > 0 ? (mcqCorrect / mcqs.length) * 100 : 0;

  // Syntax Understanding = Coding Score (Mocked for now or based on code length)
  const syntaxScore = codingTasks.length > 0 && codingTasks[0].user.length > 50 ? 90 : 40;

  // Speed Calculation (Based on timeTaken vs Limit)
  // If average time taken is < 50% of limit, speed is high.
  const avgTime = results.reduce((acc, r) => acc + (r.timeTaken || 0), 0) / total;
  const speedScore = avgTime < 30 ? 95 : (avgTime < 60 ? 75 : 50);

  // Apply to UI with transition delay
  setTimeout(() => {
      document.getElementById("logicBar").style.width = logicScore + "%";
      document.getElementById("syntaxBar").style.width = syntaxScore + "%";
      document.getElementById("speedBar").style.width = speedScore + "%";
  }, 300);

  // 4. ✅ DYNAMIC AI FEEDBACK
  const feedbackList = document.getElementById("aiFeedbackList");
  feedbackList.innerHTML = ""; // Clear loader

  const recommendations = [];
  if (accuracyPercent > 80) recommendations.push("Exceptional accuracy! You are ready for Senior-level screenings.");
  else if (accuracyPercent > 50) recommendations.push("Good foundation. Focus on edge-case handling in coding.");
  else recommendations.push("Review fundamental data structures to improve logic scores.");

  if (speedScore < 60) recommendations.push("Try timed coding challenges to improve your problem-solving speed.");
  if (syntaxScore < 60) recommendations.push(`Your ${review.meta.language} syntax needs more practice.`);

  recommendations.forEach(text => {
      const item = document.createElement("div");
      item.style.marginBottom = "12px";
      item.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles" style="color:#6fd3ff; margin-right:10px;"></i> ${text}`;
      feedbackList.appendChild(item);
  });

  // 5. ✅ UPDATE SUMMARY
  document.getElementById("summaryText").innerHTML = `
      <strong>Session:</strong> ${review.meta.type}<br>
      <strong>Focus:</strong> ${review.meta.language.toUpperCase()}<br>
      <strong>Status:</strong> ${accuracyPercent > 70 ? 'Interview Ready' : 'Needs Practice'}
  `;
});

function downloadPDF() {
  alert("Exporting High-Fidelity Performance Report...");
}