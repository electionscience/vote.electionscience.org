FROM python:3.13.2

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /code

# Install UV for dependency management
RUN pip install uv --no-cache-dir

# Copy all project files into the working directory
COPY . /code/

# Install dependencies using UV with --system flag
RUN uv pip install --system -e .

HEALTHCHECK CMD curl --fail http://localhost:8000/ || exit 1

# Use a script as the entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]