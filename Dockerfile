FROM python:3.11-slim

# -----------------------------
# System settings
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Python dependencies
# -----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Copy application code
# -----------------------------
COPY src/ ./src/
COPY alembic.ini .

# -----------------------------
# Logs directory (matches volumeMount)
# -----------------------------
RUN mkdir -p /app/logs && chmod 755 /app/logs

# -----------------------------
# Create non-root user (AKS best practice)
# -----------------------------
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# -----------------------------
# Runtime configuration
# (values come ONLY from K8s)
# -----------------------------
ENV HOST=0.0.0.0
ENV PORT=8000

# ❌ NO secrets here
# ❌ NO DATABASE_URL
# ❌ NO SECRET_KEY
# ❌ NO DEBUG defaults

# -----------------------------
# Expose application port
# -----------------------------
EXPOSE 8000

# -----------------------------
# Health check (matches K8s probes)
# -----------------------------
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# -----------------------------
# Run application
# -----------------------------
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
