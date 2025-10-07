## Anki Card Generator
This script creates (currently only) Czech Anki cards in the following format:

* Front Side
  * Word
  * Word type (adverb, noun, etc.) + gender (if noun)
  * Example sentence
* Back side
  * English translation

### How to use the script

1. First, you should create a `czech_words.csv`. This is the input file that the script reads the words from. It should look like this: 
```
mít
kamarád
dobrý
...other words
```
If you are still not certain how it should look, check the [example](czech_words.example.csv)

2. Create an API key on OpenAI's platform. We use that for getting translations. You can create one [here](https://platform.openai.com/api-keys). 
* I used gpt-4o-mini model, which is a cost-effective model for this task. The current price is $0.15/1m tokens. I would expect for around 1000 words, just a few cents in AI cost.

3. Run the following commands:
``` bash
python -m venv venv # Create virtual env in directory
source venv/bin/activate
pip install -r requirements.txt
# Optional: Set OPENAPI_KEY in env var named: OPENAI_API_KEY
export OPENAI_API_KEY=<your-api-key>
python main.py
```

4. You will now have a `czech_translations.csv` file available to you. You can go to Anki and import the file. You may need to adjust your card settings if it doesn't quite import as you'd expect. 



### Additional Options
* If you want to use a different input/output file names, you can pass them as arguments to the script. Here's the arguments:
```
-i, --input <input_file_name> # input file name, czech_words.csv = default
-o, --output <output_file_name> # Output file name, czech_translation.csv = default
-w, --workers <num> # Amount of parallel workers, 5 = default
-m, --model <model_name> # Model to use, gpt-4o-mini = default
-k, --key <open-api-key> # Open API key if not using env var, no default
```