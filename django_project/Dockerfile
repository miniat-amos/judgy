# Use base image passed as a build argument
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# Argument for competition code
ARG COMP_CODE

# Set working directory
WORKDIR /app

# Copy problems from the competition directory
COPY competitions/${COMP_CODE}/problems /tmp/problems

# Prepare problems directory
RUN for problem in /tmp/problems/*; do \
        problem_name=$(basename "$problem"); \
        mkdir -p "/app/$problem_name"; \
        if [ -d "$problem/judging_program" ] && [ "$(ls -A "$problem/judging_program")" ]; then \
            cp "$problem/judging_program/"* "/app/$problem_name/"; \
        fi; \
        if [ -d "$problem/other_files" ] && [ "$(ls -A "$problem/other_files")" ]; then \
            cp "$problem/other_files/"* "/app/$problem_name/"; \
        fi; \
    done && \
    rm -rf /tmp/problems


# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*  

# Prepare output directories and files
RUN mkdir outputs && \
    touch outputs/output.txt outputs/score.txt
