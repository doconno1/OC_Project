import requests
from bs4 import BeautifulSoup
import csv

url = "http://books.toscrape.com/catalogue/friday-night-lights-a-town-a-team-and-a-dream_158/index.html"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', class_='table table-striped')
if table:
    upc = table.find('td').text.strip()
    print("UPC:", upc)
else:
    print("upc not found")
title = soup.find('h1').text.strip()
print("Title:", title)
price_incl_tax = None   
if table:
    for row in table.find_all('tr'):
        header = row.find('th').text.strip()
        if header == 'Price (incl. tax)':
            price_incl_tax = row.find('td').text.strip()
            break
if price_incl_tax:
    print("Price (incl. tax):", price_incl_tax)
else:
    print("Price (incl. tax) not found")
price_excl_tax = None
if table:
    for row in table.find_all('tr'):
        header = row.find('th').text.strip()
        if header == 'Price (excl. tax)':
            price_excl_tax = row.find('td').text.strip()
            break
if price_excl_tax:
    print("Price (excl. tax):", price_excl_tax)
else:
    print("Price (excl. tax) not found")    
quantity_available = None
if table:
    for row in table.find_all('tr'):
        header = row.find('th').text.strip()
        if header == 'Availability':
            quantity_available = row.find('td').text.strip()
            break
if quantity_available:
    print("Availability:", quantity_available)
else:
    print("Availability not found") 
description = None
desc_header = soup.find('div', id='product_description')
if desc_header:
    description = desc_header.find_next('p').text.strip()
if description:
    print("Description:", description)
else:
    print("Description not found")  
category = None
category_header = soup.find('ul', class_='breadcrumb')
if category_header:
    links = category_header.find_all('a')
    if len(links) >= 3:
        category = links[-3].text.strip()           
if category:
    print("Category:", category)
else:
    print("Category not found")
rating = None
rating_tag = soup.find('p', class_='star-rating')
if rating_tag:
    classes = rating_tag['class']
    if len(classes) > 1:
        rating = classes[1] 
if rating:
    print("Rating:", rating)
else:
    print("Rating not found")
image_url = None
image_tag = soup.find('img')
if image_tag:
    image_url = image_tag['src']
    if image_url.startswith('../'):
        image_url = 'http://books.toscrape.com/' + image_url[3:]  # Adjust the URL
    print("Image URL:", image_url)
else:
    print("Image URL not found")
book_data = {
    'UPC': upc,
    'Title': title,
    'Price (incl. tax)': price_incl_tax,
    'Price (excl. tax)': price_excl_tax,
    'Availability': quantity_available,
    'Description': description,
    'Category': category,
    'Rating': rating,
    'Image URL': image_url
}
with open('book_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(book_data.keys())
    writer.writerow(book_data.values())
    writer.writerow(book_data.values())
# Removed incomplete 'with open' statement that caused a syntax error
