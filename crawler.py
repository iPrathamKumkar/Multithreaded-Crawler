import sys
from queue import Queue
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock
import requests
from bs4 import BeautifulSoup


class Crawler:
    DEFAULT_MAX_TIMEOUT = 10
    STATUS_OK = 200
    HTML_PARSER = 'html.parser'
    HREF = 'href'

    def __init__(self, num_workers):
        self.scraped_pages = set()
        self.to_crawl = Queue()
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.max_timeout = self.DEFAULT_MAX_TIMEOUT
        self.print_lock = Lock()
        self.visited_lock = Lock()

    def check_valid_url(self, url):
        return url.startswith('http')

    def crawl(self):
        while self.to_crawl:
            self.executor.submit(self.crawl_task, self.to_crawl.get(timeout=self.max_timeout))

    def crawl_task(self, url_to_crawl):
        try:
            response = requests.get(url_to_crawl, timeout=self.max_timeout)
        except requests.exceptions.RequestException as e:
            print('Request failed: ' + str(e))
        self.mark_visited(url_to_crawl)
        if self.response_status_ok(response):
            urls = self.get_all_urls_on_page(response)
            self.print_urls(url_to_crawl, urls)
            self.add_urls_to_crawl(urls)

    def mark_visited(self, url):
        self.visited_lock.acquire()
        self.scraped_pages.add(url)
        self.visited_lock.release()

    def response_status_ok(self, response):
        return response and response.status_code == self.STATUS_OK

    def get_all_urls_on_page(self, response):
        soup = BeautifulSoup(response.content, self.HTML_PARSER)
        a_tags = soup.find_all('a', href=True)
        urls = list()
        for tag in a_tags:
            url = tag[self.HREF]
            if self.check_valid_url(url):
                urls.append(url)
        return urls

    def add_urls_to_crawl(self, urls):
        for url in urls:
            if url not in self.scraped_pages:
                self.to_crawl.put(url)

    def print_urls(self, url, urls):
        self.print_lock.acquire()
        print(url)
        for url in urls:
            print('\t' + str(url))
        self.print_lock.release()

    def set_timeout(self, timeout_in_sec):
        self.max_timeout = timeout_in_sec


if __name__ == "__main__":
    try:
        base_url = sys.argv[1].strip()
    except IndexError:
        print('Enter a URL to start crawling\nRun the program as "python crawler.py <url>"')
        sys.exit(1)
    crawler = Crawler(4)
    if crawler.check_valid_url(base_url):
        crawler.to_crawl.put(base_url)
        crawler.crawl()
    else:
        print('Enter a valid URL\nURL must begin with http:// or https://')
        sys.exit(1)
