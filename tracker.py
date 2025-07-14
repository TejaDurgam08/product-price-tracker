import requests
from bs4 import BeautifulSoup
import html5lib
import time
import re
import os.path
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# SCOPES for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    """Authenticate and return Gmail API service"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def userInput():
    flipkart_url = input('Enter the Flipkart URL: ')
    amazon_url = input('Enter the Amazon URL: ')
    rd_url = input('Enter the Reliance Digital URL: ')
    return flipkart_url, amazon_url, rd_url

def extract_price_from_text(text):
    """Extract price as float from a string like '₹12,345'"""
    price_match = re.search(r'[\d,]+(?:\.\d+)?', text)
    if price_match:
        return float(price_match.group().replace(',', ''))
    return None

def find_price(soup, site_name):
    """Find a price dynamically"""
    possible_tags = ['div', 'span', 'p']
    possible_classes = ['price', 'Price', 'offer', 'selling', 'amount']

    for tag in possible_tags:
        for cls in possible_classes:
            price_tag = soup.find(tag, class_=re.compile(cls))
            if price_tag and extract_price_from_text(price_tag.text):
                print(f"[{site_name}] Found price in <{tag} class='{cls}'>")
                return extract_price_from_text(price_tag.text)

    price_tag = soup.find(text=re.compile(r'[₹$]\s*\d'))
    if price_tag:
        return extract_price_from_text(price_tag)
    print(f"[{site_name}] Could not find price!")
    return None

def send_email(service, to_email, subject, body):
    """Send an email using the Gmail API"""
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw_message}
    send_message = service.users().messages().send(userId="me", body=message).execute()
    print(f"Email sent. Message Id: {send_message['id']}")

def track_prices(service, flipkart_url, amazon_url, rd_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        flipkartResponse = requests.get(flipkart_url, headers=headers)
        amazonResponse = requests.get(amazon_url, headers=headers)
        RDResponse = requests.get(rd_url, headers=headers)
    except Exception as e:
        print(f"Error fetching product pages: {e}")
        return

    flipkartSoup = BeautifulSoup(flipkartResponse.content, 'html5lib')
    amazonSoup = BeautifulSoup(amazonResponse.content, 'html5lib')
    RDSoup = BeautifulSoup(RDResponse.content, 'html5lib')

    flipkartProductPrice = find_price(flipkartSoup, "Flipkart")
    amazonProductPrice = find_price(amazonSoup, "Amazon")
    RDProductPrice = find_price(RDSoup, "Reliance Digital")

    if flipkartProductPrice and amazonProductPrice and RDProductPrice:
        print(f"Flipkart Price: ₹{flipkartProductPrice}")
        print(f"Amazon Price: ₹{amazonProductPrice}")
        print(f"Reliance Digital Price: ₹{RDProductPrice}")

        if (flipkartProductPrice < amazonProductPrice) and (flipkartProductPrice < RDProductPrice):
            body = f"Flipkart price is lowest: ₹{flipkartProductPrice}"
        elif (amazonProductPrice < flipkartProductPrice) and (amazonProductPrice < RDProductPrice):
            body = f"Amazon price is lowest: ₹{amazonProductPrice}"
        else:
            body = f"Reliance Digital price is lowest: ₹{RDProductPrice}"

        send_email(service, 'example@gmail.com', 'Price Alert!', body)
    else:
        print("Could not fetch all prices. Skipping alert.")

if __name__ == '__main__':
    service = gmail_authenticate()
    flipkart_url, amazon_url, rd_url = userInput()

    try:
        while True:
            track_prices(service, flipkart_url, amazon_url, rd_url)
            time.sleep(43200) 
    except KeyboardInterrupt:
        print("\nStopped by user.")
