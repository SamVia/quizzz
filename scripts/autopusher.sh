#!/bin/bash

# 1. Handle the wait time parameter (defaults to 600 if not provided)
WAIT_TIME=${1:-600}

# Ensure the parameter is a valid number
if ! [[ "$WAIT_TIME" =~ ^[0-9]+$ ]]; then
    echo "Error: Wait time must be a number."
    echo "Usage: ./autopusher.sh [seconds]"
    exit 1
fi

# 2. Scan and store all untracked files into an array (handles spaces in filenames safely)
mapfile -t untracked_files < <(git ls-files --others --exclude-standard)

# 3. Calculate the number of untracked files
num_files=${#untracked_files[@]}

if [ "$num_files" -eq 0 ]; then
    echo "No untracked files found. Exiting."
    exit 0
fi

echo "Found $num_files untracked file(s). Starting push sequence with ${WAIT_TIME}s intervals..."

# 4. For loop over the exact number of files
for (( i=0; i<num_files; i++ )); do
    FILE="${untracked_files[$i]}"
    
    echo "[$((i+1))/$num_files] Adding untracked file: $FILE"
    
    # Add, commit, and push
    git add "$FILE"
    git commit -m "add: added $FILE"
    git push
    
    # Wait the specified seconds, unless it's the very last file
    if [ "$i" -lt $((num_files - 1)) ]; then
        echo "Successfully pushed $FILE. Waiting $WAIT_TIME seconds..."
        sleep "$WAIT_TIME"
    else
        echo "Successfully pushed $FILE. All untracked files have been pushed!"
    fi
done