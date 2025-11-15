FROM python:3.14

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /code

# Install UV for dependency management
RUN pip install uv --no-cache-dir

# Copy dependency files first for better caching
# Include README.md since pyproject.toml references it
COPY pyproject.toml uv.lock README.md ./

# Install dependencies using UV with --system flag
# Note: uv pip install uses pyproject.toml; uv.lock ensures local dev consistency
RUN uv pip install --system -e .

# Copy the rest of the project files
COPY . /code/

HEALTHCHECK CMD curl --fail http://localhost:8000/ || exit 1

# Use a script as the entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]