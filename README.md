# HRMS AI Chatbot

An AI-powered Human Resources Management System chatbot that helps HR staff members answer questions about employees, immigration/visa status, benefits, and company policies.

## Features

- **Employee Information Queries**: Search employee data by ID, join date, position, and more
- **Immigration & Visa Status**: Track H-1B, Green Card, OPT, CPT, and other visa types with expiration dates
- **Benefits Information**: Access health insurance, dental, vision, and 401k details
- **Policy Questions**: Get information about sick days, vacation, holidays, and employment agreements
- **Role-Based Access Control (RBAC)**: HR Lead vs HR Junior with different data access levels
- **Smart Context Retrieval**: RAG (Retrieval-Augmented Generation) pipeline for accurate responses
- **Local LLM**: Powered by Deepseek-R1 running on Ollama (privacy-focused, no API costs)
- **Modern UI**: React-based chat interface with real-time streaming responses
- **Dark Mode**: Toggle between light and dark themes
- **PDF Export**: Download conversation transcripts as PDF
- **Docker Support**: Run entire stack with one command

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **MongoDB**: Database for employee and HR data
- **Ollama**: Local LLM runtime (Deepseek-R1:8b)
- **LangChain**: RAG pipeline and LLM orchestration
- **Python 3.9+**

### Frontend
- **React 18** with TypeScript
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **Axios**: HTTP client for API calls

## Project Structure

```
HRMS chatbox/
├── backend/
│   ├── main.py              # FastAPI server and endpoints
│   ├── database.py          # MongoDB connection and queries
│   ├── auth.py              # Simple password authentication
│   ├── llm_handler.py       # Ollama Deepseek integration
│   ├── rag_pipeline.py      # RAG context retrieval
│   ├── load_data.py         # MongoDB data import script
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Configuration template
│   └── start.bat            # Quick start script (Windows)
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.tsx          # Main app component
│   │   ├── api.ts           # Backend API client
│   │   └── types.ts         # TypeScript definitions
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
├── MongoDB Database_HRWIKI/ # JSON data files
├── README.md                # This file
├── QUICKSTART.md            # Quick setup guide
└── PROJECT_SUMMARY.md       # Project overview
```

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.9+**
   - Download from [python.org](https://www.python.org/downloads/)

2. **Node.js 18+** and npm
   - Download from [nodejs.org](https://nodejs.org/)

3. **MongoDB**
   - **Windows**: Download from [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
   - **Mac**: `brew install mongodb-community`
   - **Linux**: `sudo apt install mongodb` or follow [official guide](https://docs.mongodb.com/manual/installation/)

4. **Ollama**
   - Download from [ollama.ai](https://ollama.ai/)
   - After installation, pull the Deepseek model:
     ```bash
     ollama pull deepseek-r1:8b
     ```

## Docker Quickstart

The easiest way to run the application is using Docker (requires Docker Desktop and Ollama installed on your host):

```bash
# 1. Make sure Ollama is running with the model
ollama pull deepseek-r1:8b
ollama serve  # or just have Ollama Desktop running

# 2. Start everything with one command
docker-compose up
```

That's it! Open http://localhost:3000 and start using the chatbot.

**Prefer manual setup?** Continue reading below for traditional installation.

---

## Manual Installation & Setup

### 1. Clone/Download the Project

If you haven't already, navigate to your project directory:
```bash
cd "C:\Users\Jizhou\Desktop\HRMS chatbox"
```

### 2. Backend Setup

#### Step 1: Create Python Virtual Environment
```bash
cd backend
python -m venv venv
```

#### Step 2: Activate Virtual Environment
- **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **Mac/Linux**:
  ```bash
  source venv/bin/activate
  ```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables
Create a `.env` file in the `backend/` directory:
```bash
copy .env.example .env
```

Edit `.env` with your settings (default values work for local development):
```env
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=HRWIKI
CHATBOT_PASSWORD=hr2025
OLLAMA_MODEL=deepseek-r1:8b
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```

#### Step 5: Start MongoDB
- **Windows**: Start MongoDB service or run `mongod`
- **Mac**: `brew services start mongodb-community`
- **Linux**: `sudo systemctl start mongod`

#### Step 6: Import Data into MongoDB
```bash
python load_data.py
```
This will import all JSON files from `MongoDB Database_HRWIKI/` into MongoDB.

#### Step 7: Start Ollama with Deepseek
In a separate terminal:
```bash
ollama run deepseek-r1:8b
```
Keep this terminal open while using the chatbot.

#### Step 8: Start Backend Server
```bash
python main.py
```
The backend will run on `http://localhost:8000`

### 3. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
```

#### Step 1: Install Dependencies
```bash
npm install
```

#### Step 2: Start Development Server
```bash
npm run dev
```
The frontend will run on `http://localhost:3000`

## Usage

1. **Access the Application**
   - Open your browser and navigate to `http://localhost:3000`

2. **Login**
   - Enter the password (default: `hr2025`)

3. **Start Asking Questions**
   - Try the suggested questions or ask your own:
     - "What is the visa status of employee 1503?"
     - "How many employees have H-1B visas expiring in 6 months?"
     - "Tell me about our health insurance plans"
     - "What are the sick day and vacation policies?"

## Example Queries

### Employee Information
- "Show me information about employee 1520"
- "Which employees joined in 2024?"
- "List employees working as Software Developers"

### Visa & Immigration
- "What's the visa status of employee 1503?"
- "Which employees have H-1B visas expiring soon?"
- "How many employees need visa sponsorship?"
- "Show me all employees with Green Cards"

### Benefits
- "What health insurance plans are available?"
- "Tell me about dental benefits"
- "What's the cost of health insurance for a family?"
- "Do we offer 401k?"

### Policies
- "How many sick days do employees get?"
- "What's the vacation policy?"
- "How many paid holidays are there?"

## API Endpoints

The backend provides the following REST API endpoints:

- `GET /` - Root endpoint with API info
- `GET /api/health` - Health check
- `POST /api/auth` - Authenticate with password
- `POST /api/chat` - Send chat message and get AI response
- `GET /api/employees/{id}` - Get employee by ID
- `GET /api/questions` - Get list of possible questions

## Configuration

### Change Password
Edit `backend/.env`:
```env
CHATBOT_PASSWORD=your_secure_password
```

### Use Different LLM Model
Edit `backend/.env`:
```env
OLLAMA_MODEL=llama2
# or any other Ollama model
```

### Adjust LLM Temperature
Edit `backend/.env`:
```env
LLM_TEMPERATURE=0.5  # Lower = more focused, Higher = more creative
```

## Troubleshooting

### Backend won't start
- **Error**: "MongoDB connection failed"
  - **Solution**: Ensure MongoDB is running. Check with `mongod --version`

- **Error**: "Ollama connection failed"
  - **Solution**: Start Ollama with `ollama run deepseek-r1:8b`

### Frontend won't connect to backend
- **Error**: "Unable to connect to server"
  - **Solution**: Ensure backend is running on port 8000
  - Check CORS settings in `backend/main.py`

### Slow responses
- Deepseek-R1:8b may take 10-30 seconds for complex queries
- Consider using a GPU for faster inference
- Reduce `LLM_MAX_TOKENS` in `.env` for quicker responses

### MongoDB data not loading
```bash
# Re-run the data loader
cd backend
python load_data.py
```

## Database Collections

The MongoDB database contains the following collections:

1. **Employee and Visa sponsorship information** (70 employees)
   - Employee ID, join date, position, salary, visa status

2. **Possible Questions Summary** (10 predefined questions)
   - Common HR queries and their answers

3. **EmploymentAgreement**
   - Contract template and policy details

4. **Medical plan summary - Price Details 2025**
   - Health insurance plans and pricing

5. **Delta Dental/Vision Benefit Summary**
   - Dental and vision insurance details

## Development

### Running Tests
```bash
# Backend tests (future)
cd backend
pytest

# Frontend tests (future)
cd frontend
npm test
```

### Building for Production

#### Using Docker (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up --build -d

# Deploy containers to:
# - AWS ECS/Fargate
# - DigitalOcean App Platform
# - Google Cloud Run
# - Azure Container Apps
```

#### Manual Build
**Backend**: Deploy FastAPI using Uvicorn, Gunicorn, or containerize
**Frontend**:
```bash
cd frontend
npm run build
```
This creates a `dist/` folder with optimized production files.

## Security Notes

- The current authentication uses a simple password (suitable for internal use)
- For production, implement JWT tokens or OAuth
- Never commit `.env` files with real credentials
- MongoDB should use authentication in production
- Use HTTPS in production

## Future Enhancements

- [ ] Advanced authentication (JWT, OAuth)
- [ ] Multi-user support with different roles
- [ ] Chat history persistence
- [ ] Export chat transcripts
- [ ] Voice input/output
- [ ] Integration with HR management systems
- [ ] Automated visa expiration notifications
- [ ] Analytics dashboard

## Contributing

This is an internal HR tool. For questions or issues, contact the HR IT team.

## License

Proprietary - Itlize Global LLC

---

**Built with**: FastAPI + React + MongoDB + Deepseek LLM

**Last Updated**: 2025-12-05
