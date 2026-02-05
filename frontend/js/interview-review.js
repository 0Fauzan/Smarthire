// ==========================================
// INTERVIEW-REVIEW.JS – FINAL STABILIZED VERSION
// ==========================================

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("smarthire_token");
    const rawData = localStorage.getItem("interviewReview");
    
    const container = document.getElementById("reviewContainer");
    const scoreEl = document.getElementById("finalScore");
    const subHeader = document.getElementById("subHeader");
    const perfText = document.getElementById("performanceText");

    // 1. Check if data exists
    if (!rawData) {
        if (container) container.innerHTML = "<p style='text-align:center; padding:50px;'>No interview data found. Please complete a session first.</p>";
        return;
    }

    const data = JSON.parse(rawData);
    const results = data.results || [];

    // 2. Update Header Info
    if (subHeader) subHeader.innerText = `${data.meta.language.toUpperCase()} Assessment • ${data.meta.date}`;
    
    // 3. Calculate MCQ Score
    const mcqs = results.filter(r => r.type === 'mcq');
    const correctMCQs = mcqs.filter(r => r.isCorrect === true).length;
    const totalScore = mcqs.length > 0 ? Math.round((correctMCQs / mcqs.length) * 100) : 0;

    if (scoreEl) scoreEl.innerText = `${totalScore}%`;
    if (perfText) {
        perfText.innerText = totalScore >= 70 ? "Ready for the next round! 🚀" : "Review the feedback below to improve.";
    }

    // 4. Render results
    if (container) {
        container.innerHTML = ""; // Clear the "Calculating results" text

        // Using a for...of loop to handle async AI calls one by one
        for (const [index, res] of results.entries()) {
            if (res.type === 'mcq') {
                renderMCQCard(container, res, index);
            } else if (res.type === 'coding') {
                await renderCodingCardWithAI(container, res, index, token, data.meta.language);
            }
        }
    }
});

// --- UI HELPERS ---

function renderMCQCard(container, res, i) {
    const card = document.createElement("div");
    card.className = `review-card ${res.isCorrect ? 'correct' : 'incorrect'}`;
    card.innerHTML = `
        <div class="status-badge ${res.isCorrect ? 'pass' : 'fail'}">
            ${res.isCorrect ? 'Correct' : 'Incorrect'}
        </div>
        <h3>Q${i + 1}: ${res.question}</h3>
        <p><strong>Your Answer:</strong> <span style="color:${res.isCorrect ? '#4ade80' : '#ff6b6b'}">${res.user || 'None'}</span></p>
        ${!res.isCorrect ? `<p style="opacity:0.8; font-size:13px;">Correct Answer: ${res.correct}</p>` : ''}
    `;
    container.appendChild(card);
}

async function renderCodingCardWithAI(container, res, i, token, lang) {
    // Create the card first with a loading state
    const card = document.createElement("div");
    card.className = "review-card coding-review";
    card.innerHTML = `
        <div class="status-badge pass">Coding Challenge</div>
        <h3>Q${i + 1}: Technical Task</h3>
        <p style="margin-bottom:15px;"><strong>Prompt:</strong> ${res.question}</p>
        
        <div id="ai-box-${i}" class="explanation-box" style="border: 1px solid var(--accent); margin-bottom:15px;">
            <i class="fa-solid fa-robot fa-spin"></i> AI is evaluating your code...
        </div>

        <div class="explanation-box" style="background:#111; color:#eee; font-family: monospace;">
            <strong>Your Submission:</strong>
            <pre style="margin-top:10px; white-space: pre-wrap;">${res.user}</pre>
        </div>
    `;
    container.appendChild(card);

    // Fetch the real AI results from backend
    try {
        const response = await fetch('http://127.0.0.1:5000/api/ai/analyze-code', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify({ 
                code: res.user, 
                language: lang, 
                question: res.question 
            })
        });

        if (!response.ok) throw new Error("AI Server Error");

        const aiResult = await response.json();
        const aiBox = document.getElementById(`ai-box-${i}`);
        
        // Update the loading box with real AI content
        aiBox.innerHTML = `
            <strong style="color:var(--accent);"><i class="fa-solid fa-wand-magic-sparkles"></i> AI Verdict: ${aiResult.verdict}</strong>
            <span style="float:right; font-weight:bold;">${aiResult.score}/100</span>
            <p style="margin-top:10px; font-size:14px; font-style:normal; opacity:1;">${aiResult.feedback}</p>
        `;
    } catch (err) {
        document.getElementById(`ai-box-${i}`).innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color:#ff6b6b"></i> AI Analysis unavailable at this moment.`;
    }
}