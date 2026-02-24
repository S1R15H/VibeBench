FROM ubuntu:22.04

# Install languages
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    nodejs npm \
    php \
    mysql-client \
    default-jre \
    git

# Install security tools
RUN pip3 install bandit
RUN npm install -g eslint

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Copy test files (if any needed for execution)
# COPY test_data/ /app/test_data/

WORKDIR /app
CMD ["/bin/bash"]
