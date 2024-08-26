#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <input_dir> [output_dir]"
  exit 1
fi



# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop through all Markdown files in the input directory
for md_file in "$input_dir"/*.md; do
  # Get the base name of the file (without the directory and extension)
  # print the nemar of the file
  echo "$md_file"
  base_name=$(basename "$md_file" .md)
  
  # Convert the Markdown file to a text file
  pandoc "$md_file" -t plain -o "$output_dir/$base_name.txt"
done

echo "Conversion complete."
