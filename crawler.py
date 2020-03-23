import sys
from queue import Queue, Empty
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import logging


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
        """
        Initialize the constructor
        """
        self.scraped_pages = set()
        self.to_crawl = Queue()
        self.print_lock = Lock()
        self.visited_lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=self.DEFAULT_MAX_WORKERS)
        logging.basicConfig(
            filename=self.DEFAULT_LOG_FILE_NAME,
            level=logging.INFO,
            format=self.LOG_FORMATTER,
            filemode="w",
            encoding = 'utf-8'
        )

    def add_urls_to_crawl(self, urls):
        """
        Put URLs in the queue for crawling
        :param urls: list
        :return: None
        """
        for url in urls:
            if url not in self.scraped_pages:
                self.to_crawl.put(url)

    def print_urls(self, url, urls):
        """
        Print the URL followed by the URLs found on that page
        :param url: str
        :param urls: list
        :return: None
        """
        self.print_lock.acquire()

        logging.info(url)
        for url in urls:
            logging.info("\t" + url)

        self.print_lock.release()

    def get_all_urls_on_page(self, response):
        """
        Get all URLs on a given page
        :param response: requests.model.Response object
        :return: list
        """
        soup = BeautifulSoup(response.content, self.HTML_PARSER)
        a_tags = soup.find_all("a", href=True)

        urls = list()
        for tag in a_tags:
            url = tag[self.HREF]
            if self.check_valid_url(url):
                urls.append(url)

        return urls

    def mark_visited(self, url):
        """
        Mark a given URL as visited
        :param url: str
        :return: None
        """
        self.visited_lock.acquire()
        self.scraped_pages.add(url)
        self.visited_lock.release()

    def parse_html(self, url, response):
        """
        Parse HTML to fetch all URLs
        Log the URLs and add them to crawl queue
        :param url: str
        :param response: requests.model.Response object
        :return: None
        """
        if response.status_code == self.STATUS_OK:
            self.mark_visited(url)
            urls = self.get_all_urls_on_page(response)
            self.print_urls(url, urls)
            self.add_urls_to_crawl(urls)

    def get_html(self, url_to_crawl):
        """
        Fetch the HTML at the given URL
        :param url_to_crawl: str
        :return: str, requests.model.Response object
        """
        try:
            response = requests.get(url_to_crawl, timeout=self.DEFAULT_MAX_TIMEOUT)
            self.parse_html(url_to_crawl, response)
        except requests.exceptions.RequestException as e:
            logging.warning(str(e))

    def start_crawler(self):
        """
        Driver method for adding crawl tasks to thread pool
        :return: None
        """
        while self.to_crawl:
            try:
                self.executor.submit(
                    self.get_html, self.to_crawl.get(timeout=self.DEFAULT_MAX_TIMEOUT)
                )
            except Empty as e:
                logging.warning(self.EMPTY_QUEUE_WARNING)
                sys.exit(1)

    def check_valid_url(self, url):
        """
        Check if given url is valid
        :param url: str
        :return: bool
        """
        return urlparse(url).scheme in {'http', 'https'}


if __name__ == "__main__":
    try:
        base_url = sys.argv[1].strip()
    except IndexError:
        print("Enter a URL to start crawling.")
        sys.exit(1)

    crawler = Crawler()

    if crawler.check_valid_url(base_url):
        crawler.to_crawl.put(base_url)
        crawler.start_crawler()
    else:
        print("Enter a valid URL.")
        sys.exit(1)
