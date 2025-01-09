# Dockerfile
FROM ghcr.io/home-assistant/amd64-base-python:3.9-alpine3.16

# Install required packages
RUN apk add --no-cache python3 py3-pip && \
    pip3 install --no-cache-dir aiohttp

# Set working directory
WORKDIR /usr/src

# Copy files
COPY run.sh /
COPY main.py /usr/src/

# Set permissions
RUN chmod a+x /run.sh

# Set environment
ENV LANG C.UTF-8

# Run script
CMD [ "/run.sh" ]
