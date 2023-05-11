# syntax=docker/dockerfile:1
FROM python:3.3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt --no-cache-dir
COPY . /code/
ENV SECRET_KEY=abcd12345
CMD python manage.py runserver 0.0.0.0:8000