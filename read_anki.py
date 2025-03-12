#!/usr/bin/env python3
import sys
import csv
import re

def extract_first_words(input_file, output_file="result.csv"):
    """
    Extract the first word from each line in the input file and write to a CSV file.
    Strips out extra characters like quotes and whitespace.
    
    Args:
        input_file (str): Path to the input file
        output_file (str): Path to the output CSV file (default: "result.csv")
    """
    first_words = []
    
    # Read the input file and extract first words
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Skip empty lines
                if line.strip():
                    # Extract the first word from the line
                    first_word = line.strip().split()[0]
                    # Clean the word by removing quotes and extra whitespace
                    cleaned_word = re.sub(r'["\'\"`]', '', first_word).strip()
                    first_words.append(cleaned_word)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Write the first words to the output CSV file
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write each word as a separate row
            for word in first_words:
                writer.writerow([word])
        print(f"Successfully extracted {len(first_words)} words to {output_file}")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        sys.exit(1)

def main():
    # Check if input file is provided as command-line argument
    if len(sys.argv) < 2:
        print("Usage: python read_anki.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    extract_first_words(input_file)

