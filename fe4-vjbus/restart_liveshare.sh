#!/bin/bash

# Kill existing Live Share sessions
pkill -f "vsls"

# Wait briefly
sleep 2

# Start a new session and extract URL
SESSION_URL=$(vsls share --once --readwrite | grep -o 'https://[^ ]*')

# Save to file
echo "$SESSION_URL" > share_link.txt

echo "$SESSION_URL"
