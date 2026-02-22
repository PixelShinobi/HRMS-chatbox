# HRMS AI Chatbot

A full-stack AI-powered HR assistant that answers employee-data and HR policy questions by combining structured database queries with LLM-driven chat workflows.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, LangChain |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Vite |
| **Database** | MongoDB |
| **LLM** | Deepseek-R1 via Ollama (local, no API costs) |
| **Infrastructure** | Docker Compose |

## Features

- **RAG Pipeline** — LangChain-based retrieval-augmented generation grounds responses in HR policy documents, reducing hallucination
- **Role-Based Access Control** — HR Lead and HR Junior roles with different data access levels across 70+ employee records
- **Streaming Chat UI** — React interface with real-time response streaming and dark mode
- **PDF Export** — Download conversation transcripts as PDF
- **Docker Deployment** — Full stack runs with `docker-compose up`

## Project Structure

```
HRMS-chatbox/
├── backend/
│   ├── main.py              # FastAPI server and endpoints
│   ├── database.py          # MongoDB connection and queries
│   ├── auth.py              # Authentication
│   ├── llm_handler.py       # Ollama/Deepseek integration
│   ├── rag_pipeline.py      # RAG context retrieval
│   ├── load_data.py         # MongoDB data import
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.tsx          # Main app
│   │   ├── api.ts           # Backend API client
│   │   └── types.ts         # TypeScript definitions
│   └── vite.config.ts
├── MongoDB Database_HRWIKI/ # HR data (JSON)
├── docker-compose.yml
└── README.md
```

## Setup

### Docker (Recommended)

```bash
# Pull the LLM model
ollama pull deepseek-r1:8b

# Start everything
docker-compose up
```

### Manual Setup

**Prerequisites:** Python 3.9+, Node.js 18+, MongoDB, Ollama

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python load_data.py         # Import HR data into MongoDB
python main.py             

# Frontend (new terminal)
cd frontend
npm install
npm run dev                
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/auth` | Authenticate |
| `POST` | `/api/chat` | Send message, get AI response |
| `GET` | `/api/employees/{id}` | Get employee by ID |
| `GET` | `/api/questions` | List suggested questions |

## Example Queries

- "What is the visa status of employee 1503?"
- "How many employees have H-1B visas expiring in 6 months?"
- "What health insurance plans are available?"
- "What's the vacation and sick day policy?"
- "List employees working as Software Developers"

## Database

MongoDB collections covering 70+ employee records:

- **Employee & Visa Information** — ID, position, salary, visa status, expiration dates
- **Medical Plan Summary** — Health, dental, and vision insurance plans and pricing
- **Employment Agreement** — Contract templates and policy details
- **Possible Questions** — Predefined HR queries and answers

## License

MIT
