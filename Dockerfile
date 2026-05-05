# Stage 1: Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (better caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Final runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the environment from the builder
COPY --from=builder /app/.venv /app/.venv
COPY ./src /app/src

# Use the virtualenv
ENV PATH="/app/.venv/bin:$PATH"

# Run the FastAPI app
CMD ["fastapi", "run", "src/interface/api/main.py", "--host", "0.0.0.0", "--port", "8000"]