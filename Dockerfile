FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.5.2 /uv /uvx /bin/

# Install the project into `/app`
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Cache warmup
RUN uv run app/_warmup.py 

ENTRYPOINT ["uv", "run", "app/infer.py"]
