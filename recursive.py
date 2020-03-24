import sys
from threading import Lock
from concurrent.futures.thread import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import time


class Crawler:
    DEFAULT_MAX_TIMEOUT = 10
    STATUS_OK = 200
    HTML_PARSER = 'html.parser'
    HREF = 'href'

    def __init__(self, num_workers):
        self.print_lock = Lock()
        self.visited_lock = Lock()
        self.scraped_pages = set()
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.max_timeout = self.DEFAULT_MAX_TIMEOUT

    def check_valid_url(self, url):
        return url.startswith('http')

    def crawl(self, url):
        self.executor.submit(self.crawl_task, url)

    def crawl_task(self, url):

        self.visited_lock.acquire()
        # print(self.scraped_pages)
        # print("url - " + url)
        if url in self.scraped_pages:
            self.visited_lock.release()
            return

        try:
            response = requests.get(url, timeout=self.max_timeout)
        except requests.exceptions.RequestException as e:
            print('Request failed: ' + str(e))

        self.mark_page_visited(url)
        self.visited_lock.release()

        if self.response_status_ok(response):
            links = self.get_all_links_on_page(response)
            # unvisited_links = self.get_unvisited_links(links)
            for link in links:
                # print("****" + link)
                self.executor.submit(self.crawl_task, link)

            self.print_urls(url, links)

    def mark_page_visited(self, url):
        # self.visited_lock.acquire()
        self.scraped_pages.add(url)
        # self.visited_lock.release()

    def response_status_ok(self, response):
        return response and response.status_code == self.STATUS_OK

    def get_all_links_on_page(self, response):
        soup = BeautifulSoup(response.content, self.HTML_PARSER)
        a_tags = soup.find_all('a', href=True)
        links = list()
        for tag in a_tags:
            url = tag[self.HREF]
            if self.check_valid_url(url):
                links.append(url)
        return links

    def get_unvisited_links(self, links):
        unvisited_links = list()
        # self.visited_lock.acquire()
        for link in links:
            if link not in self.scraped_pages:
                unvisited_links.append(link)
        # self.visited_lock.release()
        return unvisited_links

    def print_urls(self, url, links):
        self.print_lock.acquire()
        print(url)
        for link in links:
            print('\t' + str(link))
        self.print_lock.release()

    def set_timeout(self, timeout_in_sec):
        self.max_timeout = timeout_in_sec


if __name__ == "__main__":
    try:
        base_url = sys.argv[1].strip()
    except IndexError:
        print('Enter a URL to start crawling.')
        sys.exit(1)
    crawler = Crawler(4)
    if crawler.check_valid_url(base_url):
        crawler.crawl(base_url)
    else:
        print('Enter a valid url.')
        sys.exit(1)
    time.sleep(100)