import json
from urllib.parse import urljoin
from trafilatura import fetch_url, extract
import requests
from bs4 import BeautifulSoup, NavigableString, Tag

class UniCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.to_visit = []


    def fetch_html(self , url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_links(self , soup):
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

    def extract_json(url, links):
        return {
            "url": url,
            "links": links
        }

    def convert_to_json(self , url):
        html = self.fetch_html(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            links = self.extract_links(soup)
            json_content = self.extract_json(url, links)
            return json.loads(json_content)
        else:
            return None
        
    def crawl_url(self, url):
        if url in self.visited:
            return
        self.visited.add(url)

        downloaded = fetch_url(url)
        result = extract(downloaded, output_format="json", include_comments=True,
                         include_images=True, include_links=True, include_tables=True, include_formatting=True)
        result = json.loads(result)
        with open('result.json', 'w') as outfile:
            json.dump(result, outfile)
        return result
    
    def uni_crawler(self , scrape_sublinks = False):
        try:
            final_json = []
            if not self.base_url:
                raise ValueError("No base URL provided.")
            
            links_json = self.convert_to_json(self.base_url)

            if not links_json:
                self.to_visit.append(self.base_url)
                while self.to_visit:
                    next_url = self.to_visit.pop()
                    crawl_data = self.crawl_url(next_url)
                    if crawl_data:
                        final_json.append(crawl_data)
                        self.visited.add(next_url)
            else:
                # Add the links to the to_visit list
                self.to_visit.extend([
                    link['url'] for link in links_json['links'] 
                    if link['url'].startswith(self.base_url)
                ])

                while self.to_visit:
                    next_url = self.to_visit.pop()
                    if next_url in self.visited:
                        continue
                    crawl_data = self.crawl_url(next_url)
                    if crawl_data:
                        final_json.append(crawl_data)
                        links_json = self.convert_to_json(next_url)
                        if links_json:
                            if scrape_sublinks:
                                self.to_visit.extend([
                                    link['url'] for link in links_json['links'] 
                                    if link['url'].startswith(self.base_url) and link['url'] not in self.visited
                                ])
                        self.visited.add(next_url)


        

        except Exception as e:
            print(f"Error fetching {self.base_url}: {e}")
            return None