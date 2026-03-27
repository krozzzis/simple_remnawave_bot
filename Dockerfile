FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/
COPY locales/ ./locales/

RUN pip install uv && \
    uv pip install --system -r pyproject.toml

CMD ["python", "-m", "src.main"]
