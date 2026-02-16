#!/bin/bash

# Check if filename argument is provided
if [ $# -eq 0 ]; then
    echo "Error: No filename provided"
    echo "Usage: $0 <filename>"
    exit 1
fi

FILENAME="$1"

# Check if file exists
if [ ! -f "$FILENAME" ]; then
    echo "Error: $FILENAME not found in current directory"
    exit 1
fi

# Read file line by line and echo with delay
while IFS= read -r line; do
    echo "$line"
    sleep 0.1  # Small delay between lines (adjust as needed)
done < "$FILENAME"
