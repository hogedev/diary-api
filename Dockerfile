FROM python:3.13-slim

WORKDIR /app

ENV TZ=Asia/Tokyo
ENV PYTHONUNBUFFERED=1
ENV UV_CACHE_DIR=/tmp/uv-cache

RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser --no-log-init -s /usr/sbin/nologin appuser
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
RUN mkdir -p data /tmp/uv-cache && chown -R appuser:appuser /app /tmp/uv-cache

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)"

CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
