# Crawler

A Python-based web crawler built to discover and extract business contact information from websites.  
This project is designed to handle both static and dynamic pages, prioritise useful pages such as contact/about sections, and collect details like email addresses, phone numbers, and social links.

## Features

- Crawl websites starting from a seed URL
- Extract contact details such as:
  - Email addresses
  - Phone numbers
  - Social media links
- Handle both static and dynamic websites
- Use Selenium for pages that require JavaScript rendering
- Prioritise high-value pages such as:
  - `/contact`
  - `/about`
  - Facebook About pages
- Stop unnecessary crawling once valid contact details are found
- Built with a hybrid scraping approach for better coverage and efficiency

## Tech Stack

- **Python**
- **Selenium**
- **Requests / BeautifulSoup**
- **Regex** for email and phone extraction
- **Ollama / Mistral** *(planned or optional, for filtering best contact details)*

## Use Case

This crawler is designed for lead generation and business data collection workflows.  
It helps automate the process of finding publicly available contact information from company websites and related pages.

## How It Works

1. Start with a target website URL
2. Crawl key internal pages first
3. Detect useful links such as Contact, About, or social pages
4. Render dynamic pages when required using Selenium
5. Extract contact details from the page content
6. Return the best available results
7. Stop further crawling early when enough valid data has been found

## Project Structure

```bash
crawler/
│── main.py
│── crawler/
│   ├── scraper.py
│   ├── extractor.py
│   ├── parser.py
│   ├── utils.py
│   └── ...
│── requirements.txt
│── README.md
