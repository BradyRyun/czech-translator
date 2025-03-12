import csv
import os
import json
import time
import argparse
import concurrent.futures
from typing import List, Optional, TypedDict, Union
from openai import OpenAI 
from dotenv import load_dotenv

load_dotenv()


class TranslationResult(TypedDict):
    word: str
    word_type: str
    gender: Optional[str]
    translation: str
    example: str

def read_czech_words(input_file: str) -> List[str]:
    """Read Czech words from a CSV file."""
    words = []
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0].strip():  # Check if row exists and first column is not empty
                    # If the word doesn't exist in the list, add it
                    if row[0].strip() not in words:
                        words.append(row[0].strip())
    except Exception as e:
        print(f"Error reading input file: {e}")
        raise
    
    return words

def translate_word(word: str, openai_api_key: str) -> TranslationResult:
    """Send a word to OpenAI API and get translation information."""
    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can change this to a different model if needed
            messages=[
                {
                    "role": "system",
                    "content": "You are a Czech language expert. Provide information about Czech words in JSON format."
                },
                {
                    "role": "user",
                    "content": f"""
                    Analyze the Czech word "{word}" and provide the following information in JSON format:
                    - word: the original Czech word
                    - word_type: part of speech (noun, verb, adjective, adverb, preposition, conjunction, interjection, etc.)
                    - gender: for nouns only, use "ma" (masculine animated), "mi" (masculine inanimate), "n" (neuter), or "f" (feminine)
                    - translation: The English translation of the word
                    - example: A simple Czech sentence using this word
                    
                    For adjectives, use the masculine version.
                    If the word is not in nominative case, update it to be in nominative case.
                    If the word is in plural form, update it to be in singular form, unless it is not usually used in singular form. For example, rovnatka.
                    Return ONLY valid JSON with these fields, nothing else.
                    """
                }
            ],
            response_format={"type": "json_object"}
        )
        
        # Extract the JSON content from the response
        content = response.choices[0].message.content        
        result = json.loads(content)
        print(f"Translated: {word}")
        
        # Ensure all required fields are present
        word_type = result.get("word_type", "")
        gender = result.get("gender", None)
        
        # Only add gender to word_type if it's a noun
        if word_type.lower() == "noun" and gender:
            word_type = f"{word_type} ({gender})"
        
        return {
            "word": result.get("word", word),
            "word_type": word_type,
            "gender": gender,
            "translation": result.get("translation", ""),
            "example": result.get("example", ""),
        }
      
    except Exception as e:
        print(f"Error translating word '{word}': {e}")
        # Return a partial result in case of error
        return {
            "word": word,
            "word_type": "error",
            "gender": None,
            "translation": f"Error: {str(e)}",
            "example": "",
        }

def write_result_to_csv(result: TranslationResult, csv_writer) -> None:
    """Write a single translation result to the CSV file."""
    try:
        # Write row to CSV
        csv_writer.writerow({
            'word': result['word'],
            'word_type': result['word_type'],
            'translation': result['translation'],
            'example': result['example'],
        })
    except Exception as e:
        print(f"Error writing result for word '{result['word']}': {e}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Translate Czech words using OpenAI API')
    parser.add_argument('-i', '--input', type=str, default="czech_words.csv",
                        help='Input CSV file containing Czech words (default: czech_words.csv)')
    parser.add_argument('-o', '--output', type=str, default="czech_translations.csv",
                        help='Output CSV file for translations (default: czech_translations.csv)')
    parser.add_argument('-k', '--key', type=str,
                        help='OpenAI API key (default: OPENAI_API_KEY environment variable)')
    parser.add_argument('-w', '--workers', type=int, default=5,
                        help='Number of parallel workers (default: 5)')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    input_file = args.input
    output_file = args.output
    openai_api_key = args.key
    max_workers = args.workers
    
    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    print(f"Reading Czech words from {input_file}...")
    words = read_czech_words(input_file)
    print(f"Found {len(words)} words to translate")
    print(f"Using {max_workers} parallel workers")
    
    # Create a CSV file and writer
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
        # Define CSV headers
        fieldnames = ['word', 'word_type', 'translation', 'example']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        
        # Track completed words to maintain order in output file
        completed_count = 0
        
        # Process words in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all translation tasks
            future_to_word = {
                executor.submit(translate_word, word, openai_api_key): word 
                for word in words
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_word):
                word = future_to_word[future]
                try:
                    # Get the translation result
                    result = future.result()
                    
                    # Write the result to CSV immediately
                    write_result_to_csv(result, csv_writer)
                    
                    # Update progress
                    completed_count += 1
                    print(f"Completed: {word} ({completed_count}/{len(words)})")
                    
                except Exception as e:
                    print(f"Error processing word '{word}': {e}")
                    # Write error result to CSV
                    error_result = {
                        "word": word,
                        "word_type": "error",
                        "gender": None,
                        "translation": f"Error: {str(e)}",
                        "example": "",
                    }
                    write_result_to_csv(error_result, csv_writer)
                    completed_count += 1
    
    print(f"All results written to {output_file}")
    print("Done!")

if __name__ == "__main__":
    main()
