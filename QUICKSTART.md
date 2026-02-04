# Quick Start Guide

This guide will help you get the HRMS AI Chatbot running in 5 minutes.

## Prerequisites Check

Before starting, verify you have:
- [ ] Python 3.9+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] MongoDB installed and running
- [ ] Ollama installed with Deepseek model (`ollama list`)

If any are missing, see the main README.md for installation instructions.

## Quick Setup (3 Commands)

### Terminal 1: Start Ollama
```bash
ollama run deepseek-r1:8b
```
Leave this terminal open.

### Terminal 2: Setup & Start Backend

**Windows - Automated Setup (Recommended)**:
```bash
cd backend
start.bat
```
The `start.bat` script automatically creates the virtual environment, installs dependencies, sets up `.env`, and starts the server.

**Manual Setup (All platforms)**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
copy .env.example .env         # Windows
# cp .env.example .env         # Mac/Linux
python load_data.py
python main.py
```
Leave this terminal open.

### Terminal 3: Setup & Start Frontend
```bash
cd frontend
npm install
npm run dev
```

## Access the Application

1. Open browser: `http://localhost:3000`
2. Login with the password set in `backend/.env` (template default: `change_me`)
3. Start chatting!

## First Time Setup Only

If this is your first time:

1. **Import MongoDB Data** (required once):
   ```bash
   cd backend
   python load_data.py
   ```
   Press 'y' to import all files.

2. **Pull Deepseek Model** (required once):
   ```bash
   ollama pull deepseek-r1:8b
   ```

## Daily Usage

After initial setup, you only need to run:

1. **Start MongoDB** (if not auto-starting)
   ```bash
   # Windows: mongod
   # Mac: brew services start mongodb-community
   # Linux: sudo systemctl start mongod
   ```

2. **Start Ollama**
   ```bash
   ollama run deepseek-r1:8b
   ```

3. **Start Backend**

   **Windows** - Use the automated script:
   ```bash
   cd backend
   start.bat
   ```

   **Mac/Linux** - Manual activation:
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```

4. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

## Sample Questions to Try

Once logged in, try these:

1. **Employee Info**: "What is the information for employee 1503?"
2. **Visa Status**: "Which employees have H-1B visas?"
3. **Benefits**: "Tell me about the health insurance options"
4. **Policies**: "How many vacation days do employees get?"

## Troubleshooting

### "MongoDB connection failed"
→ Start MongoDB: `mongod` (Windows) or `brew services start mongodb-community` (Mac)

### "Ollama connection failed"
→ Run: `ollama run deepseek-r1:8b`

### "Unable to connect to server"
→ Make sure backend is running on port 8000

### Slow responses
→ Normal! Deepseek may take 10-30 seconds for complex queries

## Support

For detailed documentation, see README.md
For issues, contact the development team.

---
