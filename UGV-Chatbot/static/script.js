/* ============================================================
   UGV Smart Assistant — script.js
   Handles chat UI, API calls, exam routine filtering
   ============================================================ */

// ── Theme Toggle ──────────────────────────────────────────────
const themeBtn = document.getElementById("themeToggle");
const savedTheme = localStorage.getItem("ugv-theme");
if (savedTheme === "light") document.body.classList.add("light-mode");

if (themeBtn) {
  themeBtn.textContent = document.body.classList.contains("light-mode") ? "🌙" : "☀️";
  themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");
    const isLight = document.body.classList.contains("light-mode");
    themeBtn.textContent = isLight ? "🌙" : "☀️";
    localStorage.setItem("ugv-theme", isLight ? "light" : "dark");
  });
}


// ── Chat Interface ────────────────────────────────────────────
const messagesDiv  = document.getElementById("messages");
const inputEl      = document.getElementById("chatInput");
const sendBtn      = document.getElementById("sendBtn");

/** Append a message bubble to the chat */
function appendMessage(text, role) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "👤" : "🎓";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  // Convert basic markdown-like syntax
  bubble.innerHTML = formatText(text);

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  messagesDiv.appendChild(wrapper);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  return wrapper;
}

/** Simple markdown formatter: **bold**, _italic_ */
function formatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/_(.*?)_/g, "<em>$1</em>")
    .replace(/`(.*?)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
}

/** Show a typing animation bubble */
function showTyping() {
  const wrapper = document.createElement("div");
  wrapper.className = "message bot";
  wrapper.id = "typingIndicator";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "🎓";

  const indicator = document.createElement("div");
  indicator.className = "typing-indicator";
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement("div");
    dot.className = "typing-dot";
    indicator.appendChild(dot);
  }

  wrapper.appendChild(avatar);
  wrapper.appendChild(indicator);
  messagesDiv.appendChild(wrapper);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideTyping() {
  const el = document.getElementById("typingIndicator");
  if (el) el.remove();
}

/** Send message to backend */
async function sendMessage(text) {
  const message = (text || inputEl.value).trim();
  if (!message) return;

  appendMessage(message, "user");
  if (inputEl) { inputEl.value = ""; inputEl.style.height = "46px"; }
  sendBtn && (sendBtn.disabled = true);
  showTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    hideTyping();
    appendMessage(data.response || "Sorry, I couldn't process that.", "bot");
  } catch (err) {
    hideTyping();
    appendMessage("⚠️ Network error. Please check your connection.", "bot");
    console.error(err);
  } finally {
    sendBtn && (sendBtn.disabled = false);
    inputEl && inputEl.focus();
  }
}

// Event listeners for chat
if (sendBtn) sendBtn.addEventListener("click", () => sendMessage());

if (inputEl) {
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Auto-resize textarea
  inputEl.addEventListener("input", () => {
    inputEl.style.height = "46px";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + "px";
  });
}

// Suggestion chips
document.querySelectorAll(".chip").forEach(chip => {
  chip.addEventListener("click", () => sendMessage(chip.dataset.msg));
});

// Welcome message on load
window.addEventListener("load", () => {
  if (messagesDiv) {
    setTimeout(() => {
      appendMessage(
        "👋 **Assalamu Alaikum! Welcome to UGV Smart Assistant!**\n\n" +
        "I can help you with exam routines, admission info, teachers, scholarships, and more.\n\n" +
        "Try asking: _Show semester 5 exam routine_ or _When is the OOP exam?_",
        "bot"
      );
    }, 400);
  }
});


// ── Exam Routine Page ─────────────────────────────────────────
const routineContainer = document.getElementById("routineContainer");

/** Load exam routine data from API */
async function loadExamRoutine(semester = "", search = "") {
  if (!routineContainer) return;

  routineContainer.innerHTML = `<div class="empty-state"><div class="icon">⏳</div><p>Loading...</p></div>`;

  const params = new URLSearchParams();
  if (semester) params.set("semester", semester);
  if (search)   params.set("search", search);

  try {
    const res  = await fetch(`/api/exam-routine?${params}`);
    const data = await res.json();
    renderRoutine(data);
  } catch (err) {
    routineContainer.innerHTML = `<div class="empty-state"><div class="icon">❌</div><p>Failed to load. Please refresh.</p></div>`;
  }
}

/** Group by semester and render */
function renderRoutine(exams) {
  if (!routineContainer) return;
  if (exams.length === 0) {
    routineContainer.innerHTML = `<div class="empty-state"><div class="icon">🔍</div><p>No exams found matching your filter.</p></div>`;
    return;
  }

  // Group by semester
  const bySem = {};
  exams.forEach(e => {
    if (!bySem[e.semester]) bySem[e.semester] = [];
    bySem[e.semester].push(e);
  });

  let html = "";
  Object.keys(bySem).sort((a,b) => a-b).forEach(sem => {
    const rows = bySem[sem];
    html += `
      <div class="semester-block">
        <div class="semester-header" onclick="toggleSem(this)">
          <span>📚 Semester ${sem} — CSE</span>
          <span class="semester-badge">${rows.length} exams ▾</span>
        </div>
        <div class="semester-body">
          <table class="exam-table">
            <thead>
              <tr>
                <th>Course</th>
                <th>Code</th>
                <th>Date</th>
                <th>Time</th>
                <th>Room</th>
                <th>Countdown</th>
              </tr>
            </thead>
            <tbody>
              ${rows.map(e => rowHTML(e)).join("")}
            </tbody>
          </table>
        </div>
      </div>`;
  });

  routineContainer.innerHTML = html;
  startCountdowns();
}

function rowHTML(e) {
  const d = new Date(e.exam_date);
  const dateStr = d.toLocaleDateString("en-GB", { day:"2-digit", month:"short", year:"numeric", weekday:"short" });
  return `
    <tr>
      <td><strong>${e.course_name}</strong></td>
      <td><code>${e.course_code}</code></td>
      <td><span class="date-badge">${dateStr}</span></td>
      <td>${e.exam_time}</td>
      <td>${e.room}</td>
      <td><span class="countdown" data-date="${e.exam_date}">--</span></td>
    </tr>`;
}

function toggleSem(header) {
  const body = header.nextElementSibling;
  body.style.display = body.style.display === "none" ? "" : "none";
  const badge = header.querySelector(".semester-badge");
  badge.textContent = badge.textContent.includes("▾")
    ? badge.textContent.replace("▾", "▸")
    : badge.textContent.replace("▸", "▾");
}

/** Live countdown timers */
function startCountdowns() {
  document.querySelectorAll(".countdown").forEach(el => {
    const examDate = new Date(el.dataset.date + "T09:30:00");
    updateCountdown(el, examDate);
    setInterval(() => updateCountdown(el, examDate), 60000);
  });
}

function updateCountdown(el, examDate) {
  const now  = new Date();
  const diff = examDate - now;
  if (diff < 0) {
    el.textContent = "✅ Done";
    el.className = "countdown done";
    return;
  }
  const days  = Math.floor(diff / 86400000);
  const hours = Math.floor((diff % 86400000) / 3600000);
  el.className = `countdown ${days <= 3 ? "urgent" : ""}`;
  el.textContent = days > 0 ? `⏰ ${days}d ${hours}h` : `⚡ ${hours}h left`;
}

// Filter controls
const semFilter    = document.getElementById("semesterFilter");
const searchInput  = document.getElementById("searchInput");

if (semFilter)   semFilter.addEventListener("change",   () => loadExamRoutine(semFilter.value, searchInput?.value));
if (searchInput) searchInput.addEventListener("input",  () => loadExamRoutine(semFilter?.value, searchInput.value));

// Load on page if routine container exists
if (routineContainer) loadExamRoutine();


// ── Admin Page ────────────────────────────────────────────────
const adminForm = document.getElementById("addExamForm");

if (adminForm) {
  adminForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = Object.fromEntries(new FormData(adminForm).entries());
    const alertDiv = document.getElementById("adminAlert");

    try {
      const res  = await fetch("/api/admin/exam", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(formData)
      });
      const data = await res.json();
      alertDiv.className = "alert alert-success";
      alertDiv.textContent = "✅ " + data.message;
      adminForm.reset();
    } catch {
      alertDiv.className = "alert alert-error";
      alertDiv.textContent = "❌ Failed to add exam. Please try again.";
    }

    alertDiv.style.display = "block";
    setTimeout(() => alertDiv.style.display = "none", 4000);
  });
}
