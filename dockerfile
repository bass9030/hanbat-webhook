FROM python:3.10-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /usr/src/app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

ENV PATH="/usr/src/app/.venv/bin:$PATH"

COPY . .

CMD ["python", "main.py"]
