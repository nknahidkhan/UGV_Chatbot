# 🎓 UGV Smart Assistant

AI-powered university chatbot for the University of Global Village (UGV), Barishal.

## ✨ Features
- 💬 AI chatbot (Gemini API + rule-based fallback)
- 📋 Complete Winter-2026 exam routine (all 8 CSE semesters)
- ⏰ Live countdown timers for exams
- 🔍 Search and filter exam routine
- 🎓 Admission FAQ
- 📢 Notices system
- ⚙️ Admin panel to add exams
- 🌙 Dark/Light mode
- 📱 Mobile responsive

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up your Gemini API key
- Get a free key at: https://aistudio.google.com/apikey
- Edit `.env` and replace `your_gemini_api_key_here` with your key

### 3. Initialize the database
```bash
python database.py
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```

## 📁 Project Structure
```
UGV-Chatbot/
├── app.py          ← Flask backend (routes & API)
├── chatbot.py      ← AI brain (intent detection + responses)
├── database.py     ← DB setup and seeding
├── requirements.txt
├── .env            ← API keys (never commit this!)
├── templates/
│   ├── index.html       ← Chat UI
│   ├── exam_routine.html← Exam browser
│   └── admin.html       ← Admin panel
├── static/
│   ├── style.css   ← Dark mode UI
│   └── script.js   ← Frontend logic
└── data/
    └── ugv_data.json ← University knowledge base
```

## 💬 Example Chatbot Queries
- "Show semester 5 exam routine"
- "When is the Machine Learning exam?"
- "What are the admission requirements?"
- "Tell me about the CSE department"
- "What scholarships are available?"
- "Show latest notices"
- "আমার পরীক্ষার রুটিন দেখাও" (Bengali support)

## 🌐 Deploy to Render (Free)
1. Push to GitHub
2. Go to render.com → New Web Service
3. Connect your repo
4. Set environment variables (GEMINI_API_KEY)
5. Start command: `python app.py`

## 👨‍💻 Built for UGV — CSE Department
Department of Computer Science and Engineering  
University of Global Village, Barishal  
Head: Md. Riadul Islam
