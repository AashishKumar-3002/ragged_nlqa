import requests
from bs4 import BeautifulSoup
import json

def fetch_and_parse(url):
    try:
        # Fetch the web page
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract main content from <body> tag
        main_content = soup.find('body')('div', class_='main')

        return main_content

    except requests.exceptions.RequestException as e:
        print(f"Error fetching/parsing {url}: {e}")
        return None

def extract_data(url):
    # Fetch and parse the webpage
    content = fetch_and_parse(url)
    if not content:
        return None

    # Markdown format
    markdown_output = f"### Website Content from {url}\n\n```\n{content}\n```\n"

    # # JSON format
    # json_output = {
    #     "url": url,
    #     "content": content
    # }

    return markdown_output

if __name__ == "__main__":
    # Example usage
    url_to_scrape = "https://stanford-cs324.github.io/winter2022/lectures/introduction"  # Replace with your desired URL
    markdown_content = extract_data(url_to_scrape)

    # Print or save the results
    if markdown_content:
        print("Markdown Output:")
        print(markdown_content)

