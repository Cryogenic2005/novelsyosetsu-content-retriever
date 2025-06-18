# Novel Syosetsu Content Retriever

A Python tool to retrieve and translate chapters from Japanese web novels hosted on [ncode.syosetu.com](https://ncode.syosetu.com/), using Google Gemini for translation.

## Features
- Download chapters from a specified Syosetu novel link
- Translate chapters from Japanese to English using Google Gemini
- Organize raw and translated content by novel and chapter
- Configurable cooldown to avoid rate limiting
- Verbosity control for logging

## Requirements
- Python 3.11+
- Google Gemini API key

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/novelsyosetsu-content-retriever.git
   cd novelsyosetsu-content-retriever
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage
Run the script from the command line:
```sh
python main.py --novel_link <novel_link> --novel_name <novel_name> \
    [--chapters 1 2 3 ...] \
    [--cooldown_time 5] \
    [--verbosity 1]
```

- `--novel_link`: URL to the novel on ncode.syosetu.com (e.g., `https://ncode.syosetu.com/examplenovelid/`) (**required**)
- `--novel_name`: Name for the novel (used for directory structure) (**required**)
- `--chapters`: List of chapter indices to translate (default: `[1]`)
- `--cooldown_time`: Seconds to wait between requests (default: `5`)
- `--verbosity`: Logging level (0: silent, 1: basic info, 2: detailed info)

### Example
```sh
python main.py --novel_link https://ncode.syosetu.com/examplenovelid/ --novel_name "Example Novel" --chapters 1 2 3 --cooldown_time 10 --verbosity 2
```

## Directory Structure
```
chapters/
  <novel_name>/
    raw_content/           # Original Japanese text files
    raw_html/              # Original HTML files
    translation/           # Translated text files
src/
  gemini_client.py         # Handles Gemini API requests
  retriever.py             # Retrieves and parses novel chapters
  translator.py            # Manages translation workflow
main.py                    # Entry point for CLI usage
```

## License
MIT License
