import requests
from bs4 import BeautifulSoup
import csv
import re
from urllib.parse import urljoin
base_url = "http://books.toscrape.com/catalogue/category/books/sports-and-games_17/"
page_url = "index.html"
headers = {'User-Agent': 'Mozilla/5.0'} 
product_urls = []

while page_url:
    url = urljoin(base_url, page_url)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        continue
    soup = BeautifulSoup(response.text, 'html.parser')
    for h3 in soup.find_all('h3'):
        a_tag = h3.find('a')
        if a_tag and a_tag.get('href'):
            product_url = urljoin("http://books.toscrape.com/catalogue/", a_tag['href'])
            product_urls.append(product_url)
    next_li = soup.find('li', class_='next')
    if next_li and next_li.a:
        page_url = next_li.a['href']
    else:
        page_url = None
book_data = []
for url in product_urls:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    price_incl_tax = "N/A"
    price_excl_tax = "N/A"
    quantity = "N/A"
    upc = "UPC not found"
    description = "Description not found"
    category = "Category not found"
    review_rating = "Rating not found"
    image_url = "Image URL not found"
    table = soup.find('table', class_='table table-striped')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                key = cols[0].text.strip().lower().replace(' ', '_')
                value = cols[1].text.strip()
                if key == "price_including_tax":
                    price_incl_tax = value
                elif key == "price_excluding_tax":
                    price_excl_tax = value
                elif key == "number_available":
                    quantity = value
                elif key == "upc":
                    upc = value
                elif key == "product_description":
                    description = value
                elif key == "category":
                    category = value
                elif key == "review_rating":
                    review_rating = value
                elif key == "image_url":
                    image_url = value

    description_header = soup.find('div', id='product_description')
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else "Title not found"
    book_data.append({
        'UPC': upc,
        'description': description,
        'title': title,  
        'price_incl_tax': price_incl_tax,
        'price_excl_tax': price_excl_tax,
        'quantity': quantity,
        'category': category,
        'review_rating': review_rating,
        'image_url': image_url, 
        'URL': url
    })
if book_data:
    with open('books.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = book_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for book in book_data:
            writer.writerow(book)
    print("Data written to books.csv")
else:
    print("No book data found.")
