FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock
RUN poetry install --only main --only ui --only backend --all-extras

COPY ./soul_diary /app/soul_diary

ENTRYPOINT ["poetry", "run", "python", "-m", "soul_diary"]
CMD ["run"]
