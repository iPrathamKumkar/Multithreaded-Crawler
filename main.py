from queue import Queue
from crawler import Crawler

queue = Queue()
queue.put('https://www.rescale.com')
url = queue.get()
Crawler.crawl_page(url)