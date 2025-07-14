# Automated Product Price Tracker

A Python tool that scrapes product prices from multiple e-commerce websites and sends email alerts when the best price is found — using Gmail API and OAuth 2.0.

## Features

- Web scraping with Requests + BeautifulSoup
- Compare prices across Flipkart, Amazon, Reliance Digital
- Secure email alerts with Gmail API (OAuth 2.0)
- Runs on schedule with sleep loop

## Tech Stack

Python, Requests, BeautifulSoup, Gmail API

## Setup

1. Clone this repo:https://github.com/TejaDurgam08/product-price-tracker.git

2. Install dependencies:

    cd product-price-tracker    
    pip install -r requirements.txt

3. Add your `credentials.json` (Google OAuth 2.0 file) to the folder.

4. Replace the example@gmail.com with the recipient email

5. Run the script: python tracker.py


## License

MIT License
