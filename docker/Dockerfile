# ── Build stage ──────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ────────────────────────────────────────
FROM python:3.12-slim

# Timezone
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY main.py .
COPY feeds.yaml .
COPY src/ src/
COPY db/ db/

# Non-root user for security
RUN useradd --create-home appuser
USER appuser

# Default: run scheduler (production mode)
CMD ["python", "main.py"]
