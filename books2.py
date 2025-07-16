import requests
from bs4 import BeautifulSoup
import csv
import re
from urllib.parse import urljoin

base_url = "http://books.toscrape.com/"
headers = {'User-Agent': 'Mozilla/5.0'}

# Step 1: Get all category URLs from the main page
response = requests.get(base_url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'html.parser')

category_urls = []
for a in soup.select('div.side_categories ul li ul li a'):
    category_url = urljoin(base_url, a['href'])
    category_urls.append(category_url)

book_data = []

# Step 2: Loop through each category and paginate
for category_url in category_urls:
    page_url = category_url
    while page_url:
        try:
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {page_url}: {e}")
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        for h3 in soup.find_all('h3'):
            a_tag = h3.find('a')
            if a_tag and a_tag.get('href'):
                product_url = urljoin(page_url, a_tag.get('href'))
                try:
                    prod_resp = requests.get(product_url, headers=headers)
                    prod_resp.raise_for_status()
                except requests.RequestException as e:
                    print(f"Failed to fetch {product_url}: {e}")
                    continue
                prod_soup = BeautifulSoup(prod_resp.text, 'html.parser')

                price_incl_tax = "N/A"
                price_excl_tax = "N/A"
                quantity = "N/A"
                upc = "UPC not found"
                description = "Description not found"
                category = "Category not found"
                review_rating = "Rating not found"
                image_url = "Image URL not found"

                table = prod_soup.find('table', class_='table table-striped')
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        th = row.find('th')
                        td = row.find('td')
                        if th and td:
                            key = th.text.strip().lower().replace(' ', '_')
                            value = td.text.strip()
                            if key == "price_(incl._tax)":
                                price_incl_tax = value
                            elif key == "price_(excl._tax)":
                                price_excl_tax = value
                            elif key == "availability":
                                quantity = value
                            elif key == "upc":
                                upc = value

                # Description
                description_header = prod_soup.find('div', id='product_description')
                if description_header:
                    desc_p = description_header.find_next_sibling('p')
                    if desc_p:
                        description = desc_p.text.strip()

                # Category
                breadcrumb = prod_soup.find('ul', class_='breadcrumb')
                if breadcrumb:
                    category_li = breadcrumb.find_all('li')
                    if len(category_li) > 2:
                        category = category_li[2].text.strip()

                # Review rating
                rating_tag = prod_soup.find('p', class_='star-rating')
                if rating_tag:
                    classes = rating_tag.get('class', [])
                    for c in classes:
                        if c != 'star-rating':
                            review_rating = c

                # Image URL
                image_tag = prod_soup.find('img')
                if image_tag and image_tag.get('src'):
                    image_url = urljoin(product_url, image_tag['src'])

                title_tag = prod_soup.find('h1')
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
                    'URL': product_url
                })

        # Pagination for category
        next_li = soup.find('li', class_='next')
        if next_li and next_li.a:
            next_href = next_li.a['href']
            page_url = urljoin(page_url, next_href)
        else:
            page_url = None

# Write to CSV
if book_data:
    with open('all_books.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = book_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for book in book_data:
            writer.writerow(book)
    print("Data written to all_books.csv")
else:
    print("No book data found.")