import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

# URL to crawl
base_url = "https://stanford-cs324.github.io/winter2022/lectures/"

def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return None

def extract_text_between_h2_tags(soup):
    h2_tags = soup.find_all('h2')
    text_list = []

    for h2 in h2_tags:
        next_element = h2.find_next_sibling()
        text = ""
        while next_element and next_element.name != 'h2':
            if next_element.name in ['p', 'a', 'span', 'div', 'li', 'strong', 'em']:
                text += ' ' + next_element.get_text(strip=True)
            next_element = next_element.find_next_sibling()

        text_list.append(text.strip())

    return text_list

def parse_links(page_content, base_url):
    soup = BeautifulSoup(page_content, 'html.parser')
    data = {}

    # Extract all links
    links = soup.find_all('a', href=True)
    data['links'] = {}

    for link in links:
        href = link['href']
        text = link.get_text(strip=True)
        full_url = urljoin(base_url, href)

        # Only consider links that start with the base URL
        if full_url.startswith(base_url):
            data['links'][full_url] = text

    # Extract text between h2 tags
    data['text_between_h2'] = extract_text_between_h2_tags(soup)

    return data

def crawl(url, visited):
    if url in visited:
        return None
    visited.add(url)

    print(f"Visiting: {url}")

    page_content = get_page_content(url)
    if page_content:
        data = parse_links(page_content, url)
        all_data[url] = data

        for link in data['links']:
            if link not in visited:
                crawl(link, visited)
    else:
        return None

all_data = {}
visited = set()

# Start crawling from the base URL
crawl(base_url, visited)

# Save the data to a JSON file
with open('stanford_cs324_datas.json', 'w') as f:
    json.dump(all_data, f, indent=4)

print("Crawling completed. Data saved to stanford_cs324_data.json")
