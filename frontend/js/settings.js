// ==========================================
// SETTINGS.JS – CONFIGURATION LOGIC
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    
    // 1. Load User Data
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if(user.name) document.getElementById("setName").value = user.name;
    if(user.email) document.getElementById("setEmail").value = user.email;

    // 2. Sync Dark Mode Switch
    const themeSwitch = document.getElementById("darkModeSwitch");
    const currentTheme = localStorage.getItem("theme") || "dark";
    if (themeSwitch) {
        themeSwitch.checked = (currentTheme === "dark");
        
        themeSwitch.addEventListener("change", () => {
            const newTheme = themeSwitch.checked ? "dark" : "light";
            localStorage.setItem("theme", newTheme);
            document.body.classList.toggle("light", newTheme === "light");
            
            // Also update the navbar button icon if it exists
            const navBtn = document.querySelector("#themeToggle i");
            if(navBtn) navBtn.className = newTheme === "light" ? "fa-solid fa-sun" : "fa-solid fa-moon";
        });
    }

    // 3. Handle Profile Update
    document.getElementById("accountForm").addEventListener("submit", (e) => {
        e.preventDefault();
        
        const updatedUser = {
            ...user,
            name: document.getElementById("setName").value,
            email: document.getElementById("setEmail").value
        };

        localStorage.setItem("user", JSON.stringify(updatedUser));
        
        // Visual Feedback
        const status = document.getElementById("accStatus");
        status.innerText = "Settings saved successfully! ✅";
        status.style.color = "#4ade80";
        setTimeout(() => status.innerText = "", 3000);
    });
});

// --- TAB SWITCHING ---
function showTab(tabId, navElement) {
    // Hide all tabs
    document.querySelectorAll('.tab-pane').forEach(tab => tab.classList.remove('active'));
    // Deactivate nav items
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

    // Show selected
    document.getElementById(tabId).classList.add('active');
    navElement.classList.add('active');
}

// --- DATA EXPORT ---
function exportData() {
    const data = JSON.stringify(localStorage);
    const blob = new Blob([data], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `smarthire_data_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
}

// --- DELETE ACCOUNT ---
function deleteAccount() {
    const confirmDelete = confirm("Are you sure? This will wipe all your Interview History and Resume data.");
    if (confirmDelete) {
        localStorage.clear();
        alert("Account deleted. Redirecting to home.");
        window.location.href = "index.html";
    }
}