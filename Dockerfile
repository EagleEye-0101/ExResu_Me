FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Tectonic LaTeX compiler (for /api/latex/*)
RUN curl -fsSL "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-musl.tar.gz" \
    | tar -xz -C /usr/local/bin --strip-components=1 tectonic-0.15.0-x86_64-unknown-linux-musl/tectonic \
    && chmod +x /usr/local/bin/tectonic

COPY pyproject.toml README.md ./
COPY resume_engine ./resume_engine
COPY api ./api
COPY cli ./cli

RUN pip install --no-cache-dir -e .

RUN python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

EXPOSE 8000

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
