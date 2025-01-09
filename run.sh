# run.sh
#!/usr/bin/with-contenv bashio

bashio::log.info "Starting PSE Energy Status addon..."

# Make sure Python and pip are installed
apk add --no-cache python3 py3-pip

# Install required packages
pip3 install aiohttp

bashio::log.info "Running main script..."
python3 /usr/src/main.py
