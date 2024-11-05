FROM python:3.12

# Install required system packages
# RUN apt-get update && apt-get install -y default-mysql-client

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install setuptools 

# Copy your application code
COPY ./django_project .

# Copy the entrypoint script
COPY ./entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["sh", "/entrypoint.sh"]