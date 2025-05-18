# FastAPI + React Monorepo

This repository contains a full-stack application with a FastAPI backend and React frontend organized in a monorepo structure.

## Project Structure

```
/project-root
  /backend             # FastAPI backend code
    /app               # Backend application code
    run.py             # Backend startup script
    Dockerfile         # Backend Docker configuration
  /frontend
    /chatbot-ui        # React frontend code
      Dockerfile       # Frontend Docker configuration
  /scripts             # Helper scripts
    start-dev.cmd      # Script to start dev environment
    start-prod.cmd     # Script to start production
  docker-compose.yml   # Docker compose configuration
```

## Getting Started

### Development Mode

To start the application in development mode (with hot reloading):

```bash
# Using the convenience script (Windows)
scripts/start-dev.cmd

# Or manually
# Terminal 1 - Start Backend
cd backend
python run.py

# Terminal 2 - Start Frontend
cd frontend/chatbot-ui
npm start
```

This will:
- Start the backend on http://localhost:8000
- Start the frontend on http://localhost:3000

### Production Mode

To build and run the application for production:

```bash
# Using the convenience script (Windows)
scripts/start-prod.cmd

# Or manually
# Build the frontend
cd frontend/chatbot-ui
npm run build

# Run the backend
cd backend
python run.py
```

## Docker Support

This project includes Docker configuration for containerized development and deployment.

### Start with Docker Compose

```bash
# Start both services
docker-compose up

# Or build and start
docker-compose up --build
```

## API Documentation

When the backend is running, the API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Setup

1. Backend environment:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Frontend environment:
   ```bash
   cd frontend/chatbot-ui
   npm install
