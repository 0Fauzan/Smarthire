// ==========================================
// RESUME.JS – BACKEND CONNECTED
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    const resumeCard = document.getElementById("resumeCard");
    const resumeInput = document.getElementById("resumeInput");
    const atsCard = document.getElementById("atsCard");

    const token = localStorage.getItem("smarthire_token");
    if (!token) return;

    if (resumeCard && resumeInput) {
        resumeCard.addEventListener("click", () => resumeInput.click());
        resumeInput.addEventListener("change", handleFileUpload);
    }
    
    if (atsCard) {
        atsCard.addEventListener("click", (e) => {
            if (e.target.closest("#improveResumeBtn")) return;
            atsCard.classList.toggle("expanded");
        });
    }

    fetchResume(token);
});

// --- API FUNCTIONS ---

async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const token = localStorage.getItem("smarthire_token");
    const formData = new FormData();
    formData.append('resume', file);

    document.getElementById("resumeStatus").innerText = "Uploading & Analyzing...";

    try {
        const response = await fetch('http://127.0.0.1:5000/api/resume/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "Upload failed.");
            document.getElementById("resumeStatus").innerText = "Upload failed.";
            return;
        }
        
        document.getElementById("resumeStatus").innerText = `Uploaded ✓ (${data.resume.filename})`;
        updateATSUI(data.resume);
        
        // Update local storage for Insights page
        localStorage.setItem("resume_analysis_data", JSON.stringify({
            score: data.resume.ats_score,
            filename: data.resume.filename,
            date: new Date().toLocaleDateString(),
            logic: data.resume.ats_score + 5,
            syntax: data.resume.ats_score - 5,
            speed: data.resume.ats_score
        }));


    } catch (error) {
        console.error("Upload error:", error);
        alert("Server error during upload.");
    }
}

async function fetchResume(token) {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/resume', {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 404) {
            document.getElementById("resumeStatus").innerText = "No resume uploaded yet.";
            return;
        }

        const data = await response.json();
        
        document.getElementById("resumeStatus").innerText = `Uploaded ✓ (${data.filename})`;
        updateATSUI(data);

    } catch (error) {
        console.error("Fetch resume error:", error);
    }
}

// --- UI UPDATE HELPER (Frontend simulation for breakdown) ---
function updateATSUI(resumeData) {
    const score = resumeData.ats_score || 0;
    
    const elements = {
        atsValue: document.getElementById("atsValue"),
        atsMini: document.getElementById("atsMiniValue"),
        kw: document.getElementById("kwScore"),
        fmt: document.getElementById("fmtScore"),
        sec: document.getElementById("secScore"),
        status: document.getElementById("atsStatus")
    };

    if (elements.atsValue) elements.atsValue.innerText = score;
    if (elements.atsMini) elements.atsMini.innerText = score;

    // Simulate breakdown based on score
    if (elements.kw) elements.kw.innerText = (score + 3) + "%";
    if (elements.fmt) elements.fmt.innerText = (score - 5) + "%";
    if (elements.sec) elements.sec.innerText = (score + 2) + "%";
    if (elements.status) elements.status.innerText = score > 80 ? "Strong Match" : "Good Match";
}