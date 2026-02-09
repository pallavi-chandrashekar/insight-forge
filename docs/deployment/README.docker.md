# Docker Setup for InsightForge

## Quick Start with Docker

### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop/))
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Steps to Run

1. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your Anthropic API key
   # API_KEY=your-actual-api-key-here
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - FastAPI backend (port 8000)
   - React frontend (port 5173)

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Useful Docker Commands

```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v

# Rebuild containers after code changes
docker-compose up --build

# Restart a specific service
docker-compose restart backend

# Check service status
docker-compose ps
```

### First Time Setup

1. The database will be automatically created when you start the services
2. Tables will be created on first API request
3. Create your first user by visiting http://localhost:5173/register

### Development Workflow

The Docker setup includes volume mounts for hot-reloading:
- Backend changes auto-reload (uvicorn --reload)
- Frontend changes auto-reload (Vite HMR)
- Database persists in a Docker volume

### Troubleshooting

**Port already in use:**
```bash
# Find process using port
lsof -i :5173  # or :8000, :5432

# Kill the process or change ports in docker-compose.yml
```

**Database connection errors:**
```bash
# Check if database is healthy
docker-compose ps

# Restart database
docker-compose restart db
```

**Backend errors:**
```bash
# Check backend logs
docker-compose logs backend
```

### Clean Start

To completely reset everything:
```bash
# Stop and remove everything
docker-compose down -v

# Start fresh
docker-compose up --build
```
