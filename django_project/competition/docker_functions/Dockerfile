ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y \
    bash \
    coreutils \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Create runner user with no home, no shell login
RUN useradd -M -s /bin/false -u 1001 runner

WORKDIR /app

COPY judge.sh .

RUN chmod +x judge.sh \
    # # runner needs to read/execute the script, but not modify it
    && chown runner:runner judge.sh \
    && chmod 750 judge.sh 

USER runner