import sys
from queue import Queue, Empty
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock
import requests
from bs4 import BeautifulSoup
import logging


class Crawler:
    """A Crawler class to fetch URLs and output results to a log"""
    DEFAULT_MAX_WORKERS = 4
    DEFAULT_MAX_TIMEOUT = 10
    DEFAULT_LOG_FILE_NAME = 'crawler.log'
    STATUS_OK = 200
    HTML_PARSER = 'html.parser'
    HREF = 'href'
    LOG_FORMATTER = '%(levelname)s: %(message)s'
    EMPTY_QUEUE_WARNING = 'Crawler queue empty. Exiting program.'

    def __init__(self):
        """
        Initialize the constructor
        """
        self.scraped_pages = set()
        self.to_crawl = Queue()
        self.max_workers = self.DEFAULT_MAX_WORKERS
        self.max_timeout = self.DEFAULT_MAX_TIMEOUT
        self.log_file_name = self.DEFAULT_LOG_FILE_NAME
        self.print_lock = Lock()
        self.visited_lock = Lock()

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

    def add_urls_to_crawl(self, urls):
        """
        Put URLs in the queue for crawling
        :param urls: list
        :return: None
        """
        for url in urls:
            if url not in self.scraped_pages:
                self.to_crawl.put(url)

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

    def response_status_ok(self, response):
        """
        Check if the response is valid
        :param response: requests.model.Response object
        :return: bool
        """
        return response and response.status_code == self.STATUS_OK

    def mark_visited(self, url):
        """
        Mark a given URL as visited
        :param url: str
        :return: None
        """
        self.visited_lock.acquire()
        self.scraped_pages.add(url)
        self.visited_lock.release()

    def crawl_task(self, url_to_crawl):
        """
        Perform the fetching, parsing and logging tasks for a given URL
        :param url_to_crawl: str
        :return: None
        """
        try:
            response = requests.get(url_to_crawl, timeout=self.max_timeout)

            if self.response_status_ok(response):
                self.mark_visited(url_to_crawl)
                urls = self.get_all_urls_on_page(response)
                self.print_urls(url_to_crawl, urls)
                self.add_urls_to_crawl(urls)

        except requests.exceptions.RequestException as e:
            logging.warning(str(e))

    def start_crawler(self):
        """
        Driver method for adding crawl tasks to thread pool
        :return: None
        """
        executor = ThreadPoolExecutor(max_workers=self.max_workers)
        logging.basicConfig(
            filename=self.log_file_name,
            level=logging.INFO,
            format=self.LOG_FORMATTER,
            filemode="w",
        )

        while self.to_crawl:
            try:
                executor.submit(
                    self.crawl_task, self.to_crawl.get(timeout=self.max_timeout)
                )
            except Empty as e:
                logging.warning(self.EMPTY_QUEUE_WARNING)
                sys.exit(1)

    def check_valid_url(self, url):
        """
        Check if input url is valid
        :param url: str
        :return: bool
        """
        return url.startswith("http")


if __name__ == "__main__":
    try:
        base_url = sys.argv[1].strip()
    except IndexError:
        print('Enter a URL to start crawling.')
        sys.exit(1)

    crawler = Crawler()

    if crawler.check_valid_url(base_url):
        crawler.to_crawl.put(base_url)
        crawler.start_crawler()
    else:
        print('Enter a valid URL.')
        sys.exit(1)
