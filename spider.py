import requests
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse


class Spider:

    def __init__(self, base_url):
        self.base_url = base_url
        self.pool = ThreadPoolExecutor(max_workers=4)
        self.scraped_pages = set()
        self.to_crawl = Queue()
        self.to_crawl.put(self.base_url)

    @staticmethod
    def check_valid_url(url):
        if urlparse(url).scheme in {'http', 'https'}:
            return True
        return

    def parse_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            if Spider.check_valid_url(url) and url not in self.scraped_pages:
                self.to_crawl.put(url)

    def post_scrape_callback(self, response):
        result = response.result()
        if result and result.status_code == 200:
            self.parse_links(result.text)

    def scrape_page(self, url):
        try:
            response = requests.get(url, timeout=10)
            return response
        except requests.RequestException:
            return

    def run_scraper(self):
        while True:
            try:
                target_url = self.to_crawl.get()
                if target_url not in self.scraped_pages:
                    print(target_url)
                    self.scraped_pages.add(target_url)
                    job = self.pool.submit(self.scrape_page, target_url)
                    job.add_done_callback(self.post_scrape_callback)
            except Empty:
                return
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    spider = Spider('https://www.rescale.com')
    spider.run_scraper()