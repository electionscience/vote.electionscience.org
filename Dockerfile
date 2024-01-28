FROM python:3.8.16

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt --no-cache-dir
COPY . /code/
COPY prod.sqlite3 /data/
ENV SECRET_KEY=abcd12345
CMD python manage.py runserver 0.0.0.0:8000