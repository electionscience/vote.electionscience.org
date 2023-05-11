# syntax=docker/dockerfile:1
FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY pyproject.toml /code/
RUN pip install poetry --no-cache-dir
RUN poetry shell && poetry install
COPY . /code/
ENV SECRET_KEY=abcd12345
CMD python manage.py runserver 0.0.0.0:8000