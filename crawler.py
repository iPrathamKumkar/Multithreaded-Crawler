from urllib.request import urlopen
from link_finder import LinkFinder


class Crawler:

    queue = set()
    crawled = set()

    @staticmethod
    def crawl_page(page_url):
        if page_url not in Crawler.crawled:
            Crawler.add_links_to_queue(Crawler.gather_links(page_url))

    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode(response.info().get_content_charset())
            finder = LinkFinder(page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        print(finder.page_links())
        return finder.page_links()

    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if url in Crawler.queue or url in Crawler.crawled:
                continue
            Crawler.queue.add(url)
