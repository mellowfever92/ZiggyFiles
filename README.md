# ZiggyFiles

A collection of files and scripts from the **ZiggyProject** — an AI-assisted astrology report automation effort built entirely through LLM prompt engineering, with no traditional coding background required.

**Project Date:** November 2024 – December 2024  
**Language:** Python 100%  
**Author:** David McCarthy ([@mellowfever92](https://github.com/mellowfever92))

---

## Overview

The ZiggyProject was built to help a Tropical Astrology business automate the creation of in-depth, personalized **Natal Birth Chart reports**. Given only a client's name, date of birth, birth time, and location, the system generates a detailed ~60-page reading powered by GPT-4o and a custom AI persona called **Professor Orion** (a.k.a. "Ziggy").

All code in this repository was produced through careful prompt engineering using an advanced reasoning LLM — demonstrating that complex, functional software can be built without traditional programming skills, given the right approach and tooling.

---

## Repository Structure

```
ZiggyFiles/
├── Ziggy_Main_Project/          # Core production scripts and assets
│   ├── astrology_gpt_generator_alternate.py   # Main script: scrapes astro-seek.com, generates batch JSONL, processes output to .docx
│   ├── astrology_report_batch_gen.py          # Alternate script: fetches birth chart data from astrology.dailyom.com API
│   ├── astrology_selenium.py                  # Selenium-based scraper for birth chart data from astro-seek.com
│   ├── testbatch.jsonl                        # Sample batch JSONL for testing
│   ├── ZiggyProject Chat History/             # Full LLM chat history documenting the prompt-engineering process
│   └── ReadMe.md                              # Project-specific notes
├── Completed Parsing/           # Parsed knowledge base files used by the Ziggy AI persona
│   ├── ZiggyBotDegrees.txt                    # Degree-level astrological interpretations
│   └── ZiggyExtraDrees.txt                    # Supplementary astrological content
├── Script Test/                 # Testing sandbox: sample outputs, test JSONL files, and helper scripts
│   ├── canvasedits.py
│   ├── jsonl_convert.py
│   ├── ziggyboss.py
│   ├── david_mccarthy.jsonl / .json / .docx   # Example generated report for testing
│   └── results.jsonl
├── Proxy Prompt Protection.txt  # System prompt instructions for protecting the Ziggy AI persona's knowledge base
└── ZiggyBotHealth.txt           # Core health/persona instructions for the Ziggy chatbot
```

---

## How It Works

1. **Input:** Provide a client's name, date of birth (MM-DD-YYYY), birth hour, birth minute, AM/PM, and birth location.
2. **Data Fetch:** The script queries an astrology API or scrapes [astro-seek.com](https://astro-seek.com) to retrieve planetary positions, house placements, and aspects for the natal chart.
3. **Batch Generation:** 49 GPT-4o API requests are constructed in JSONL format, each targeting a specific section of the birth chart reading.
4. **Report Assembly:** Once the OpenAI Batch API processes the requests, the script compiles all responses into a single formatted `.docx` file — the final personalized report.

---

## Scripts

### `astrology_gpt_generator_alternate.py`
The primary production script. Scrapes birth chart data from astro-seek.com via BeautifulSoup, builds 49 batch API requests for the Ziggy/Professor Orion persona, and assembles the `.docx` output.

**Usage:**
```bash
# Step 1: Generate the batch JSONL file
python astrology_gpt_generator_alternate.py generate --name "Jane Doe" --birthdate 06-15-1990 --birthhour 3 --birthminute 42 --ampm PM --address "Los Angeles, CA, USA"

# Step 2: Process the batch output into a .docx report
python astrology_gpt_generator_alternate.py process --input janedoe.jsonl --output janedoe_reading.docx
```

**Dependencies:** `requests`, `beautifulsoup4`, `python-docx`, `argparse`  
**Also requires:** A Google Maps API key (for geocoding birth location)

### `astrology_report_batch_gen.py`
An alternate version that fetches birth chart data from the `astrology.dailyom.com` public API instead of scraping.

### `astrology_selenium.py`
A Selenium-based scraper for automating form submission on astro-seek.com to retrieve birth chart data.

**Dependencies:** `selenium`, `beautifulsoup4`

---

## Key Files

| File | Description |
|------|-------------|
| `ZiggyBotHealth.txt` | Persona and behavioral instructions for the Ziggy AI chatbot |
| `Proxy Prompt Protection.txt` | System-level prompt guardrails to protect the AI's knowledge base from being exposed |
| `Completed Parsing/ZiggyBotDegrees.txt` | Parsed astrology degree interpretations used by the AI |
| `Ziggy_Main_Project/ZiggyProject Chat History/` | Full conversation log of the prompt-engineering sessions that built this project |

---

## Requirements

```
requests
beautifulsoup4
python-docx
selenium
argparse
```

Install with:
```bash
pip install requests beautifulsoup4 python-docx selenium
```

You will also need:
- An **OpenAI API key** with Batch API access (GPT-4o)
- A **Google Maps API key** for birth location geocoding

---

## Background & Philosophy

This project was built from scratch using only prompt engineering — no prior coding experience was used to write the scripts. The full development chat history is included in `Ziggy_Main_Project/ZiggyProject Chat History/` for anyone who wants to study the process.

The success of this project supports the idea that with a strong reasoning LLM and careful attention to detail, advanced automation tools are within reach for non-programmers.

---

## License

No license specified. All rights reserved by the author.
