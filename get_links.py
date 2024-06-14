import requests
import json
from bs4 import BeautifulSoup, NavigableString, Tag

def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None



def extract_links(soup):
    # Remove nav bar
    for nav in soup.find_all('nav'):
        nav.decompose()

    links = []
    for link in soup.find_all('a', href=True):
        links.append({
            'url': link['href'],
            'title': link.string
        })
    return links

def extract_markdown(links):
    markdown_lines = []
    for link in links:
        markdown_lines.append(f"*   [{link['title']}]({link['url']})")
    return "\n".join(markdown_lines)

def extract_json(url, links):
    return {
        "url": url,
        "links": links
    }

def convert_to_markdown_and_json(url):
    html = fetch_html(url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        links = extract_links(soup)
        markdown_content = extract_markdown(links)
        json_content = extract_json(url, links)
        return markdown_content, json_content
    else:
        return None, None

# Example usage
url = 'https://stanford-cs324.github.io/winter2022/lectures'
markdown_output, json_output = convert_to_markdown_and_json(url)

if markdown_output and json_output:
    print("Markdown Output:")
    print(markdown_output)
    print("\n")
    
    print("JSON Output:")
    print(json.dumps(json_output, indent=4))
else:
    print("Failed to convert website to markdown and JSON.")

