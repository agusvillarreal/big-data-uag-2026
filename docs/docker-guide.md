# Docker Beginner's Guide

## What is Docker?

Docker is a platform that allows you to package applications and their dependencies into isolated units called **containers**. Containers are lightweight, portable, and run consistently across different environments.

---

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Image** | A read-only template with instructions for creating a container. Think of it as a blueprint. |
| **Container** | A running instance of an image. You can have multiple containers from the same image. |
| **Dockerfile** | A text file with instructions to build a Docker image. |
| **Volume** | Persistent storage that survives container restarts and removals. |
| **Network** | Allows containers to communicate with each other. |
| **Registry** | A repository for storing and distributing Docker images (e.g., Docker Hub). |

---

## Installation

### macOS
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Or use Homebrew:
brew install --cask docker
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

### Verify Installation
```bash
docker --version
docker compose version
```

---

## Basic Docker Commands

### Working with Images

```bash
# Search for images on Docker Hub
docker search python

# Download an image
docker pull python:3.11-slim
docker pull postgres:15          # PostgreSQL database

# List downloaded images
docker images

# Remove an image
docker rmi python:3.11-slim
docker rmi -f python:3.11-slim   # Force remove

# Remove all unused images
docker image prune -a
```

### Working with Containers

```bash
# Run a container
docker run python:3.11-slim python --version

# Run in detached mode (background)
docker run -d python:3.11-slim sleep infinity

# Run with a custom name
docker run -d --name my-python python:3.11-slim sleep infinity

# Run with port mapping (host:container)
docker run -d -p 5000:5000 --name flask-app my-flask-image

# Run with environment variables
docker run -d -e FLASK_DEBUG=1 my-flask-image

# Run with volume mount
docker run -d -v /host/path:/container/path my-flask-image

# Run interactively with terminal
docker run -it python:3.11-slim bash

# Run and auto-remove when stopped
docker run --rm python:3.11-slim python -c "print('Hello Docker!')"

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop flask-app

# Start a stopped container
docker start flask-app

# Restart a container
docker restart flask-app

# Remove a container
docker rm flask-app
docker rm -f flask-app           # Force remove running container

# Remove all stopped containers
docker container prune
```

### Docker Logs

```bash
# View container logs
docker logs flask-app

# Follow logs in real-time
docker logs -f flask-app

# Show last N lines
docker logs --tail 100 flask-app

# Show logs with timestamps
docker logs -t flask-app

# Combine options
docker logs -f --tail 50 -t flask-app
```

### Docker Exec

```bash
# Execute a command in a running container
docker exec flask-app ls /app

# Open an interactive shell
docker exec -it flask-app bash
docker exec -it flask-app sh      # For Alpine-based images

# Run as specific user
docker exec -u root -it flask-app bash

# Set environment variables
docker exec -e MY_VAR=value flask-app env

# Run a Python script in container
docker exec flask-app python -c "print('Hello from container!')"
```

### Inspect and Debug

```bash
# View container details
docker inspect flask-app

# View container resource usage
docker stats
docker stats flask-app

# View running processes in a container
docker top flask-app

# Copy files between host and container
docker cp flask-app:/app/data.json ./data.json
docker cp ./myfile.txt flask-app:/app/
```

---

## Dockerfile Basics

A Dockerfile defines how to build an image.

### Example: Flask Application

```dockerfile
# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Command to run
CMD ["python", "app.py"]
```

### Example: Jupyter Notebook for Data Science

```dockerfile
FROM python:3.11-slim

WORKDIR /notebooks

# Install data science packages
RUN pip install --no-cache-dir \
    jupyter \
    jupyterlab \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scikit-learn

COPY . .

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
```

### Build and Run

```bash
# Build an image from Dockerfile
docker build -t flask-app:1.0 .

# Build with different Dockerfile
docker build -f Dockerfile.jupyter -t jupyter-data:1.0 .

# Build without cache
docker build --no-cache -t flask-app:1.0 .

# Run the Flask application
docker run -d -p 5000:5000 --name myapp flask-app:1.0

# Run Jupyter Lab
docker run -d -p 8888:8888 -v $(pwd)/notebooks:/notebooks jupyter-data:1.0
```

---

## Docker Compose

Docker Compose allows you to define and run multi-container applications using a YAML file.

### Example: docker-compose.yml (Flask + PostgreSQL + Jupyter)

```yaml
version: "3.8"

services:
  flask-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://admin:secret@database:5432/myapp
    depends_on:
      - database
    volumes:
      - .:/app

  jupyter:
    build:
      context: .
      dockerfile: Dockerfile.jupyter
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/notebooks
    depends_on:
      - database

  database:
    image: postgres:15
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=myapp
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  db_data:
```

### Docker Compose Commands

```bash
# Start all services
docker compose up

# Start in detached mode
docker compose up -d

# Start specific service
docker compose up -d database

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# View running services
docker compose ps

# View logs
docker compose logs
docker compose logs -f flask-app      # Follow specific service

# Execute command in service
docker compose exec flask-app bash

# Run a Python command in service
docker compose exec flask-app python -c "print('Hello!')"

# Rebuild images
docker compose build
docker compose up -d --build    # Rebuild and restart

# Scale a service
docker compose up -d --scale flask-app=3

# Restart services
docker compose restart
docker compose restart flask-app
```

---

## Volumes and Networks

### Volumes

```bash
# Create a volume
docker volume create mydata

# List volumes
docker volume ls

# Inspect a volume
docker volume inspect mydata

# Remove a volume
docker volume rm mydata

# Remove all unused volumes
docker volume prune

# Use volume in container
docker run -d -v mydata:/app/data flask-app
```

### Networks

```bash
# Create a network
docker network create mynetwork

# List networks
docker network ls

# Inspect a network
docker network inspect mynetwork

# Connect container to network
docker network connect mynetwork flask-app

# Disconnect from network
docker network disconnect mynetwork flask-app

# Run container on specific network
docker run -d --network mynetwork flask-app

# Remove network
docker network rm mynetwork
```

---

## Useful Command Combinations

```bash
# Stop all running containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# Full cleanup (containers, images, volumes, networks)
docker system prune -a --volumes

# View disk usage
docker system df

# Export container as tar
docker export flask-app > backup.tar

# Save image as tar
docker save flask-app:1.0 > flask-app.tar

# Load image from tar
docker load < flask-app.tar
```

---

## Common Patterns

### Development with Hot Reload (Flask)

```yaml
# docker-compose.dev.yml
version: "3.8"
services:
  flask-app:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - .:/app
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
```

Run with:
```bash
docker compose -f docker-compose.dev.yml up
```

### Using .dockerignore

Create a `.dockerignore` file to exclude files from the build context:

```
__pycache__
*.pyc
.git
.env
*.log
Dockerfile
docker-compose.yml
.dockerignore
README.md
.venv
venv
.pytest_cache
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker run -d -p 5000:5000 flask-app` | Run container in background with port mapping |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers |
| `docker logs -f <container>` | Follow container logs |
| `docker exec -it <container> bash` | Open shell in container |
| `docker stop <container>` | Stop container |
| `docker rm <container>` | Remove container |
| `docker images` | List images |
| `docker rmi <image>` | Remove image |
| `docker build -t name:tag .` | Build image from Dockerfile |
| `docker compose up -d` | Start services in background |
| `docker compose down` | Stop and remove services |
| `docker compose logs -f` | Follow all service logs |
| `docker system prune -a` | Clean up unused resources |

---

## Quick Demo (Copy-Paste Ready)

Run these commands in order. All files will be created in a temporary directory and cleaned up at the end.

### Step 1: Create demo directory and files

```bash
mkdir -p /tmp/flask-demo && cd /tmp/flask-demo
```

```bash
cat > app.py << 'EOF'
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Hello from Flask in Docker!', 'status': 'running'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
```

```bash
cat > requirements.txt << 'EOF'
flask==3.0.0
EOF
```

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
EOF
```

### Step 2: Build the image

```bash
docker build -t my-flask-image .
```

### Step 3: Run the container

```bash
docker run -d -p 5000:5000 --name flask-app my-flask-image
```

### Step 4: Test it

```bash
curl http://localhost:5000
```

Expected output:
```json
{"message":"Hello from Flask in Docker!","status":"running"}
```

### Step 5: View logs

```bash
docker logs flask-app
```

### Step 6: Clean up everything

```bash
docker stop flask-app && docker rm flask-app && docker rmi my-flask-image && rm -rf /tmp/flask-demo
```

---

## Next Steps

1. Practice building images for your Flask applications
2. Learn about multi-stage builds for smaller images
3. Explore Docker registries (Docker Hub, GitHub Container Registry)
4. Study container orchestration with Kubernetes or Docker Swarm
5. Learn about Docker security best practices
