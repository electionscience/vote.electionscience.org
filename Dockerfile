FROM python:3.14.0a4

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /code

# Install Poetry
# Note: Consider locking the Poetry version for consistent builds
ENV POETRY_VERSION=1.8.4
RUN pip install "poetry==$POETRY_VERSION" --no-cache-dir

# Copy the project files into the working directory
COPY pyproject.toml poetry.lock* /code/

# Configure Poetry
# - Do not create a virtual environment inside the Docker container
# - Do not ask any interactive question (like the confirmation of package installation)
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

# Install runtime dependencies using Poetry
RUN poetry install --only main --no-root

# Copy the rest of the project files into the working directory
COPY . /code/

HEALTHCHECK CMD curl --fail http://localhost:8000/ || exit 1

# Use a script as the entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]