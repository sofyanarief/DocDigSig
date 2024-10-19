# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./project /app

# Install system dependencies for pdf processing
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    libssl-dev \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
RUN pip install\
    Flask \
    pycryptodome \
    pymupdf \
    mysql-connector-python \
    pyhanko[full]\
    pdfquery\
    gevent\
    six

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "Server.py"]
