FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.cache/pypoetry /root/.cache/pypoetry
COPY --from=builder /root/.local /root/.local

COPY --from=builder /app/pyproject.toml /app/poetry.lock ./

ENV PATH="/root/.local/bin:$PATH"

COPY . .

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000