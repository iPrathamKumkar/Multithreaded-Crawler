import sys
from queue import Queue, Empty
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock
import requests
from bs4 import BeautifulSoup
import logging


class Crawler:
    DEFAULT_MAX_WORKERS = 4
    DEFAULT_MAX_TIMEOUT = 10
    DEFAULT_LOG_FILE_NAME = "crawler.log"
    STATUS_OK = 200
    HTML_PARSER = "html.parser"
    HREF = "href"

    def __init__(self):
        self.scraped_pages = set()
        self.to_crawl = Queue()
        self.max_workers = self.DEFAULT_MAX_WORKERS
        self.max_timeout = self.DEFAULT_MAX_TIMEOUT
        self.log_file_name = self.DEFAULT_LOG_FILE_NAME
        self.print_lock = Lock()
        self.visited_lock = Lock()

    def print_urls(self, url, urls):
        self.print_lock.acquire()

        logging.info(url)
        for url in urls:
            logging.info("\t" + url)

        self.print_lock.release()

    def add_urls_to_crawl(self, urls):
        for url in urls:
            if url not in self.scraped_pages:
                self.to_crawl.put(url)

    def get_all_urls_on_page(self, response):
        soup = BeautifulSoup(response.content, self.HTML_PARSER)
        a_tags = soup.find_all("a", href=True)

        urls = list()
        for tag in a_tags:
            url = tag[self.HREF]
            if self.check_valid_url(url):
                urls.append(url)

        return urls

    def response_status_ok(self, response):
        return response and response.status_code == self.STATUS_OK

    def mark_visited(self, url):
        self.visited_lock.acquire()
        self.scraped_pages.add(url)
        self.visited_lock.release()

    def crawl_task(self, url_to_crawl):
        try:
            response = requests.get(url_to_crawl, timeout=self.max_timeout)

            if self.response_status_ok(response):
                self.mark_visited(url_to_crawl)
                urls = self.get_all_urls_on_page(response)
                self.print_urls(url_to_crawl, urls)
                self.add_urls_to_crawl(urls)

        except requests.exceptions.RequestException as e:
            logging.warning("Failed to get " + url_to_crawl)

    def start_crawler(self):
        executor = ThreadPoolExecutor(max_workers=self.max_workers)
        logging.basicConfig(
            filename=self.log_file_name,
            level=logging.INFO,
            format="%(levelname)s: %(message)s",
            filemode="w",
        )

        while self.to_crawl:
            try:
                executor.submit(
                    self.crawl_task, self.to_crawl.get(timeout=self.max_timeout)
                )
            except Empty:
                logging.warning('No URL to crawl')
                sys.exit(1)

    def check_valid_url(self, url):
        return url.startswith("http")


if __name__ == "__main__":
    try:
        base_url = sys.argv[1].strip()
    except IndexError:
        print("Enter a URL to start crawling")
        sys.exit(1)

    crawler = Crawler()

    if crawler.check_valid_url(base_url):
        crawler.to_crawl.put(base_url)
        crawler.start_crawler()
    else:
        print("Enter a valid URL")
        sys.exit(1)
