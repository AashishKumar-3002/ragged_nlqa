import json
from urllib.parse import urljoin
from trafilatura import fetch_url, extract
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

class UniCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.to_visit = Queue()

    def fetch_html(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_links(self ,url , soup):
        # Remove nav bar
        for nav in soup.find_all('nav'):
            nav.decompose()

        links = []
        for link in soup.find_all('a', href=True):
            links.append({
                'url': urljoin(url, link['href']),
                'title': link.string
            })
        return links

    def extract_json(self, url, links):
        return {
            "url": url,
            "links": links
        }

    def convert_to_json(self, url):
        html = self.fetch_html(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            links = self.extract_links(url , soup)
            json_content = self.extract_json(url, links)
            return json_content
        else:
            return None

    def crawl_url(self, url):
        if url in self.visited:
            return None
        self.visited.add(url)

        downloaded = fetch_url(url)
        result = extract(downloaded, output_format="json", include_comments=True,
                         include_images=True, include_links=True, include_tables=True, include_formatting=True)
        if result:
            result = json.loads(result)
            print(f"Visited: {url}")
            return result
        return None

    def worker(self, scrape_sublinks , found_sublinks):
        while not self.to_visit.empty():
            next_url = self.to_visit.get()
            try:
                if next_url not in self.visited:
                    crawl_data = self.crawl_url(next_url)

                    if not found_sublinks or scrape_sublinks:
                        sublinks_citation = set()
                        sublinks_external = set()
                        sublinks_json = self.convert_to_json(next_url)
                        
                        if sublinks_json:
                            sublinks = [
                                link['url'] for link in sublinks_json['links']
                                if link['url'].startswith(self.base_url) and not link['url'] in self.base_url and link['url'] != self.base_url
                            ]
                            for sublink in sublinks:
                                if next_url in sublink and sublink not in sublinks_citation:
                                    sublinks_citation.add(sublink)
                                if next_url not in sublink and sublink not in sublinks_external:
                                    sublinks_external.add(sublink)
                                
                            
                            # Add the sublinks to the sublinks list in the form of dict with url and also add a condtition to check if the sublink contains the url if yes the add it to the list in citation section , else in external links
                            crawl_data['metadata'] = {
                                'url': next_url,
                                'sublinks_citation': list(sublinks_citation),
                                'sublinks_external': list(sublinks_external)
                            }

                            
                            print(f"no of links to visit: {self.to_visit.qsize()}"
                                    f"no of links visited: {len(self.visited)}")
                            print(f"Links to visit are: {self.to_visit.queue}")
                            print(f"Links visited are: {self.visited}")
                    
                    if crawl_data:
                        self.final_json.append(crawl_data)

            finally:
                self.to_visit.task_done()

    def uni_crawler(self, scrape_sublinks=False, max_workers=5):
        try:
            self.final_json = []
            found_sublinks = False
            if not self.base_url:
                raise ValueError("No base URL provided.")

            links_json = self.convert_to_json(self.base_url)
            print(links_json)

            if not links_json:
                self.to_visit.put(self.base_url)
            else:
                found_sublinks = True
                self.to_visit.put(self.base_url)
                initial_links = [
                    link['url'] for link in links_json['links']
                    if link['url'].startswith(self.base_url) and not link['url'] in self.base_url and link['url'] != self.base_url and f"{self.base_url}#" not in link['url']
                ]

                for link in initial_links:
                    self.to_visit.put(link)
            

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for _ in range(max_workers):
                    executor.submit(self.worker, scrape_sublinks , found_sublinks)

            self.to_visit.join()

            return self.final_json

        except Exception as e:
            print(f"Error fetching {self.base_url}: {e}")
            return None

# Example usage
if __name__ == "__main__":
    url = 'https://stanford-cs324.github.io/winter2022/lectures/'
    crawler = UniCrawler(url)
    # final_links = crawler.convert_to_json(url)
    # print(final_links)
    final_json = crawler.uni_crawler(scrape_sublinks=True)

    if final_json:
        with open('final_result.json', 'w') as outfile:
            json.dump(final_json, outfile)
