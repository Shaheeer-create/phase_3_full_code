# Quick Start Guide - AI Chatbot Phase 3

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Neon PostgreSQL account (already configured)
- Gemini API key

---

## 📦 Installation

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_actual_api_key_here
```

**Get Gemini API Key:**
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key and paste it in `backend/.env`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Environment is already configured in .env.local
```

---

## 🏃 Running the Application

### Terminal 1: Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8001
```

### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

---

## 🧪 Quick Tests

### Test 1: Basic Chat
1. Navigate to http://localhost:3000/chat
2. Click "+ New Conversation"
3. Type: "Hello! Can you help me manage my tasks?"
4. Verify AI responds with streaming

### Test 2: Create Task
1. Type: "Create a task to buy groceries"
2. Verify green "Created Task" card appears
3. Go to /tasks page and verify task exists

### Test 3: List Tasks
1. Type: "What tasks do I have?"
2. Verify blue "Listed Tasks" card shows your tasks

### Test 4: Update Task
1. Type: "Mark task 1 as completed"
2. Verify task updates on /tasks page

---

## 🎯 Features Implemented

- ✅ Real-time streaming chat
- ✅ Task management via natural language
- ✅ Conversation management
- ✅ Auto-generated titles
- ✅ Usage tracking
- ✅ Tool execution visualization
- ✅ User data isolation

---

## 🐛 Troubleshooting

**Issue: "GEMINI_API_KEY not set"**
- Add your API key to `backend/.env`

**Issue: "401 Unauthorized"**
- Logout and login again

**Issue: "Chat not loading"**
- Check backend is running on port 8001
- Check browser console for errors

---

## 📚 Documentation

- Phase 1 Summary: `PHASE_1_IMPLEMENTATION_SUMMARY.md`
- Backend Guide: `backend/CLAUDE.md`
- Frontend Guide: `frontend/CLAUDE.md`

