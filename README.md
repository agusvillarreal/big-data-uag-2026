# Big Data UAG 2026

Repository for Big Data course materials and projects.

## Contents

- Docker guides and examples
- Big data tools and configurations
- Course projects

## Documentation

- [Docker Beginner's Guide](docs/docker-guide.md) - Complete guide to Docker, containers, images, and Docker Compose

## Examples

The `examples/` directory contains ready-to-use templates:

### Docker Templates
- `examples/docker/Dockerfile.example` - Flask application Dockerfile template
- `examples/docker/Dockerfile.jupyter.example` - Jupyter Lab Dockerfile for data science
- `examples/docker/docker-compose.example.yml` - Multi-service Docker Compose (Flask + Jupyter + PostgreSQL)
- `examples/docker/.dockerignore.example` - Dockerignore template

### Python Examples
- `examples/docker/app.py.example` - Sample Flask application
- `examples/docker/requirements.txt.example` - Python dependencies for Flask
- `examples/docker/sample_notebook.ipynb.example` - Sample Jupyter notebook for data analysis

## Getting Started

Clone this repository:

```bash
git clone https://github.com/agusvillarreal/big-data-uag-2026.git
cd big-data-uag-2026
```

## Quick Start with Docker

1. Install Docker on your system (see [Docker Guide](docs/docker-guide.md#installation))
2. Copy example files to your project:
   ```bash
   cp examples/docker/Dockerfile.example ./Dockerfile
   cp examples/docker/docker-compose.example.yml ./docker-compose.yml
   cp examples/docker/.dockerignore.example ./.dockerignore
   cp examples/docker/app.py.example ./app.py
   cp examples/docker/requirements.txt.example ./requirements.txt
   ```
3. Build and run:
   ```bash
   docker compose up -d
   ```
4. Access your services:
   - Flask app: http://localhost:5000
   - Jupyter Lab: http://localhost:8888

## Running Jupyter for Data Analysis

```bash
# Copy Jupyter Dockerfile
cp examples/docker/Dockerfile.jupyter.example ./Dockerfile.jupyter

# Create notebooks directory
mkdir -p notebooks

# Copy sample notebook
cp examples/docker/sample_notebook.ipynb.example ./notebooks/sample_notebook.ipynb

# Start with docker compose
docker compose up -d jupyter
```
