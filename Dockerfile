FROM python:3.11-bookworm as builder

ARG POETRY_VERSION=1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry==${POETRY_VERSION}

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN touch README.md
RUN poetry install --no-root && rm -rf ${POETRY_CACHE_DIR}
COPY src ./src
RUN poetry install

FROM python:3.11-slim-bookworm as runtime

RUN apt update
RUN apt install cron -y

ENV VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH \
    PYTHONPATH=/app/src:$PYTHONPATH

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

RUN echo "*/15 * 31 12 * /app/.venv/bin/python /app/src/newyear_tootgen/post.py > /tmp/stdout 2> /tmp/stderr" >> crontab
RUN echo "*/15 * 1 1 * /app/.venv/bin/python /app/src/newyear_tootgen/post.py > /tmp/stdout 2> /tmp/stderr" >> crontab
RUN echo "0 0 31 12 * /app/.venv/bin/python /app/src/newyear_tootgen/gen.py > /tmp/stdout 2> /tmp/stderr" >> crontab
RUN crontab crontab

COPY src ./app/src
COPY entrypoint.sh ./app/entrypoint.sh
RUN chmod +x ./app/entrypoint.sh

WORKDIR /app

CMD [ "./entrypoint.sh" ]