#!/bin/bash
# Heartbeat Service for GPG Agent Socket

echo "Starting GPG Agent Socket Heartbeat Service..."

while true; do
    # Microscopic NOP ping to keep the socket alive
    echo "NOP" > /dev/null
    sleep 60
done
