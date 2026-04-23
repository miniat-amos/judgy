ARG BASE_IMAGE
FROM ${BASE_IMAGE}
# install minimal tools
RUN apt-get update && apt-get install -y \
    bash \
    coreutils \
    python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy judge script
COPY judge.sh .
RUN chmod +x judge.sh

