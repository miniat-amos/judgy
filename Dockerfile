FROM python:3.12

# Install required system packages
RUN apt-get update && \
    apt-get install -y default-mysql-client && \
    RUN pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*


# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install setuptools 

# Install Docker
RUN curl -fsSL https://get.docker.com | bash

# Install Compose
RUN VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r '.tag_name') \
    && curl -L "https://github.com/docker/compose/releases/download/$VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose


# Copy your application code
COPY ./django_project .

# Copy the entrypoint script
COPY ./entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]