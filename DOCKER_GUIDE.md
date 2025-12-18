# Docker Guide for HRMS AI Chatbot

This guide explains how to run the HRMS AI Chatbot using Docker.

## Prerequisites

1. **Install Docker Desktop**
   - Windows: Download from https://www.docker.com/products/docker-desktop/
   - Install and restart your computer
   - Make sure Docker Desktop is running (system tray icon)

2. **Install Ollama** (runs on host, not in Docker)
   - Download from https://ollama.ai
   - After installation, pull the model:
     ```bash
     ollama pull deepseek-r1:8b
     ```

## Quick Start (One Command!)

```bash
# Navigate to project directory
cd "C:\Users\Jizhou\Desktop\HRMS chatbox"

# Start everything with Docker Compose
docker-compose up
```

That's it! The application will start:
- MongoDB: http://localhost:27017
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

## What Happens When You Run `docker-compose up`?

1. **Downloads images** (first time only):
   - MongoDB official image
   - Python base image
   - Node.js base image

2. **Builds containers** (first time only):
   - Backend container with Python + FastAPI
   - Frontend container with Node.js + Vite

3. **Starts services**:
   - MongoDB database
   - Backend API server (with hot reload)
   - Frontend dev server (with hot reload)

4. **Loads database**:
   - Backend connects to MongoDB
   - Loads HR data from JSON files

## Development Workflow

### Start Application
```bash
docker-compose up
```

### Edit Code
- Edit any `.py` file in `backend/` → Backend auto-reloads ✅
- Edit any `.tsx` file in `frontend/` → Frontend auto-reloads ✅
- Changes appear instantly (no rebuild needed!)

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Follow logs (real-time)
docker-compose logs -f backend
```

### Stop Application
Press `Ctrl+C` in the terminal, or:
```bash
docker-compose down
```

### Rebuild (Only When Dependencies Change)
```bash
# You added a new npm package
# You added a new Python package
# You changed Dockerfile

docker-compose up --build
```

## Common Commands

| Command | What It Does |
|---------|--------------|
| `docker-compose up` | Start all services |
| `docker-compose up -d` | Start in background (detached) |
| `docker-compose down` | Stop all services |
| `docker-compose down -v` | Stop and remove database data |
| `docker-compose logs` | View logs |
| `docker-compose ps` | See running containers |
| `docker-compose restart backend` | Restart backend only |
| `docker-compose up --build` | Rebuild and start |

## Project Structure

```
HRMS chatbox/
├── docker-compose.yml          # Orchestrates all services
├── backend/
│   ├── Dockerfile             # Backend container definition
│   ├── .dockerignore          # Files to exclude
│   └── ... (Python code)
├── frontend/
│   ├── Dockerfile             # Frontend container definition
│   ├── .dockerignore          # Files to exclude
│   └── ... (React code)
```

## How It Works

### Container Architecture

```
┌─────────────────────────────────────────────────┐
│                Docker Network                    │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ MongoDB  │  │ Backend  │  │ Frontend │     │
│  │          │  │          │  │          │     │
│  │ Port     │←─│ Port     │←─│ Port     │     │
│  │ 27017    │  │ 8000     │  │ 3000     │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│                     │                           │
│                     ↓                           │
│              ┌──────────────┐                  │
│              │ Ollama (Host)│                  │
│              │ Port 11434   │                  │
│              └──────────────┘                  │
└─────────────────────────────────────────────────┘
```

### Volume Mounting (Hot Reload)

```
Your Computer              Docker Container
─────────────              ────────────────
backend/
├── main.py        ←→     /app/main.py
├── auth.py        ←→     /app/auth.py
└── ...            ←→     /app/...

[You edit main.py]
       ↓
[Container sees change]
       ↓
[Uvicorn auto-reloads]
       ↓
[Changes live immediately!]
```

## Troubleshooting

### Port Already in Use
```
Error: Bind for 0.0.0.0:3000 failed: port is already allocated
```

**Solution:** Stop other services or change ports in `docker-compose.yml`

### Ollama Connection Failed
```
Error: Connection refused to http://host.docker.internal:11434
```

**Solution:**
1. Make sure Ollama is running on your host machine
2. Check Ollama is on port 11434: `ollama list`

### Container Won't Start
```bash
# Check logs for errors
docker-compose logs backend

# Restart containers
docker-compose restart
```

### Need Fresh Start
```bash
# Stop everything and remove containers
docker-compose down

# Remove database data too (careful!)
docker-compose down -v

# Start fresh
docker-compose up --build
```

## When to Rebuild

| Scenario | Need Rebuild? | Command |
|----------|--------------|---------|
| Edit Python/JS code | ❌ No | Just save file |
| Add npm package | ✅ Yes | `docker-compose up --build` |
| Add Python package | ✅ Yes | `docker-compose up --build` |
| Edit requirements.txt | ✅ Yes | `docker-compose up --build` |
| Edit package.json | ✅ Yes | `docker-compose up --build` |
| Edit Dockerfile | ✅ Yes | `docker-compose up --build` |
| Edit docker-compose.yml | ✅ Yes | `docker-compose up --build` |

## Benefits of Using Docker

✅ **Easy Setup** - One command to run everything
✅ **Consistent Environment** - Works the same on any computer
✅ **Easy Deployment** - Same containers work on AWS, DigitalOcean, etc.
✅ **Isolated** - Doesn't mess with your system Python/Node
✅ **Easy Cleanup** - `docker-compose down` removes everything

## Next Steps

Once comfortable with Docker:
1. Deploy to cloud (AWS, DigitalOcean)
2. Add production optimizations
3. Set up CI/CD pipelines
4. Scale horizontally (multiple backend instances)

## Need Help?

- Docker documentation: https://docs.docker.com
- Docker Compose: https://docs.docker.com/compose
- Project issues: Check logs with `docker-compose logs`
