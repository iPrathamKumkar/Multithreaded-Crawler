import os
import socket
import unittest
from crawler import Crawler


class TestCrawler(unittest.TestCase):

    def test_crawler(self):
        os.system('python -m http.server 80')
        test_file_url = 'http://localhost/TestFiles/index.html'
        Crawler.start_crawler(test_file_url)


if __name__ == '__main__':
    unittest.main()