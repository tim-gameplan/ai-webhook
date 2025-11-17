#!/bin/bash
# Start webhook client with environment variables loaded

# Load .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
fi

# Start the client
python3 client/client.py
