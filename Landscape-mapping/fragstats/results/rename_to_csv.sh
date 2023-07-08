#!/bin/bash

# Define the file extensions to be renamed
extensions=("class" "land")

# Iterate through the files in the current directory
for file in *; do
    # Get the file extension
    extension="${file##*.}"

    # Check if the extension is in the list of extensions to be renamed
    if [[ " ${extensions[@]} " =~ " ${extension} " ]]; then
        # Append the corresponding suffix to the new file name
        new_file="${file%.*}_${extension}.csv"

        # Rename the file
        mv "$file" "$new_file"
        echo "Renamed $file to $new_file"
    fi
done
