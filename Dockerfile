FROM python:3.11-slim

WORKDIR /app

# Install system deps + Node.js for frontend build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (no sentence-transformers in prod to save RAM)
COPY requirements.txt requirements-render.txt ./
RUN pip install --no-cache-dir -r requirements-render.txt

# Build React frontend
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm install

COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# Copy backend code
COPY app/ ./app/
COPY execution/ ./execution/
COPY .env.example .gitignore ./

# Use lightweight embeddings (chromadb built-in) to fit in 512MB RAM
ENV LIGHTWEIGHT_EMBEDDINGS=true

VOLUME /app/chroma_data

EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
