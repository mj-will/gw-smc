#!/usr/bin/env
# Find all ini files in current directory and submit them
for ini in $(find . -maxdepth 1 -name "*.ini"); do
    echo "Submitting $ini"
    bilby_pipe ${ini} --submit
done