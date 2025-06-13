#!/usr/bin/env
# Find all ini files in current directory and submit them
for ini in $(find . -maxdepth 1 -name "*.ini"); do
    # skip inis that include scaling in the name
    if [[ $ini == *"scaling"* ]]; then
        continue
    fi
    if [[ $ini == *"debug"* ]]; then
        continue
    fi
    echo "Submitting $ini"
    bilby_pipe ${ini} --submit
done
