import logging
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Empty, Queue
from threading import Lock
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class Crawler:
    """A Crawler class to fetch URLs and log the results"""

    DEFAULT_MAX_WORKERS = 4
    DEFAULT_MAX_TIMEOUT = 10
    DEFAULT_LOG_FILE_NAME = "crawler.log"
    LOG_FORMATTER = "%(levelname)s: %(message)s"
    STATUS_OK = 200
    HTML_PARSER = "html.parser"
    HREF = "href"
    EMPTY_QUEUE_WARNING = "Crawler queue empty. Exiting program."

    def __init__(self):
        self.scraped_pages = set()
        self.to_crawl = Queue()
        self.print_lock = Lock()
        self.visited_lock = Lock()
        self.executor = ThreadPoolExecutor(
            max_workers=self.DEFAULT_MAX_WORKERS)
        self.logger = self.instantiate_logger()

    def instantiate_logger(self):
        """
        Initialize logger for the Crawler class
        :return: logging.Logger object
        """
        logger = logging.getLogger("Crawler")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(self.DEFAULT_LOG_FILE_NAME, "w", "utf-8")
        handler.setFormatter(logging.Formatter(self.LOG_FORMATTER))
        logger.addHandler(handler)

        return logger

    def print_urls(self, url, urls):
        """
        Print the URL followed by the URLs found on that page
        :param url: str
        :param urls: list
        """
        self.print_lock.acquire()

        self.logger.info(url)
        for url in urls:
            self.logger.info("\t" + url)

        self.print_lock.release()

    def get_all_urls_on_page(self, html):
        """
        Get all URLs on a given page
        :param html: requests.model.Response object
        :return: list
        """
        soup = BeautifulSoup(html, self.HTML_PARSER)
        a_tags = soup.find_all("a", href=True)

        urls = list()
        for tag in a_tags:
            url = tag[self.HREF]
            if self.check_valid_url(url):
                urls.append(url)

        return urls

    def parse_html(self, url, html):
        """
        Parse HTML to fetch all URLs, print them, and add queue them for crawling
        Log the URLs and add them to crawl queue
        :param url: str
        :param html: requests.model.Response object
        """
        urls = self.get_all_urls_on_page(html)

        self.print_urls(url, urls)

        for url in urls:
            self.to_crawl.put(url)

    def get_html(self, url_to_crawl):
        """
        Fetch the HTML at the given URL
        :param url_to_crawl: str
        """
        self.visited_lock.acquire()

        if url_to_crawl in self.scraped_pages:
            self.visited_lock.release()
            return

        self.scraped_pages.add(url_to_crawl)
        self.visited_lock.release()

        try:
            response = requests.get(
                url_to_crawl, timeout=self.DEFAULT_MAX_TIMEOUT)
            if response.status_code == self.STATUS_OK:
                self.parse_html(url_to_crawl, response.text)
        except requests.exceptions.RequestException as e:
            self.logger.warning(str(e))

    def start_crawler(self, start_url):
        """
        Add URLs to thread pool for crawling
        """
        self.to_crawl.put(start_url)
        while self.to_crawl:
            try:
                self.executor.submit(
                    self.get_html, self.to_crawl.get(
                        timeout=self.DEFAULT_MAX_TIMEOUT)
                )
            except Empty as e:
                self.logger.warning(self.EMPTY_QUEUE_WARNING)
                sys.exit(1)

    def check_valid_url(self, url):
        """
        Check if given url is valid
        :param url: str
        :return: bool
        """
        return urlparse(url).scheme in {"http", "https"}


def main():
    """Driver method"""
    try:
        base_url = sys.argv[1].strip()
    except IndexError:
        print("Enter a URL to start crawling.")
        sys.exit(1)

    crawler = Crawler()

    if crawler.check_valid_url(base_url):
        crawler.start_crawler(base_url)
    else:
        print("Enter a valid URL.")
        sys.exit(1)


if __name__ == "__main__":
    main()
