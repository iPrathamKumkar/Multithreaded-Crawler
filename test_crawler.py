import collections
import unittest
import requests
from crawler import Crawler
from http.server import SimpleHTTPRequestHandler, HTTPServer
from threading import Thread


class TestCrawler(unittest.TestCase):
    SERVER_ADDRESS = "localhost"
    PORT = 8080
    TEST_URL = "http://localhost:8080/TestFiles/index.html"

    def setUp(self):
        self.crawl = Crawler()

        server_address = (self.SERVER_ADDRESS, self.PORT)

        self.httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
        Thread(target=self.httpd.serve_forever).start()

    def tearDown(self):
        self.httpd.shutdown()

    def test_get_all_urls_on_page(self):
        expected_urls = [
            "http://localhost:8080/TestFiles/index.html",
            "http://localhost:8080/TestFiles/index.html",
            "http://localhost:8080/TestFiles/products.html",
            "http://localhost:8080/TestFiles/about.html",
            "http://localhost:8080/TestFiles/contact.html",
            "http://localhost:8080/TestFiles/products.html",
        ]

        html = requests.get(self.TEST_URL).text
        result = self.crawl.get_all_urls_on_page(html)

        self.assertListEqual(sorted(result), sorted(expected_urls))

    def test_log_output(self):
        expected_map = {
            "http://localhost:8080/TestFiles/index.html": [
                "http://localhost:8080/TestFiles/index.html",
                "http://localhost:8080/TestFiles/index.html",
                "http://localhost:8080/TestFiles/products.html",
                "http://localhost:8080/TestFiles/about.html",
                "http://localhost:8080/TestFiles/contact.html",
                "http://localhost:8080/TestFiles/products.html",
            ],
            "http://localhost:8080/TestFiles/contact.html": [
                "http://localhost:8080:8080/TestFiles/index.html",
                "http://localhost:8080:8080/TestFiles/index.html",
                "http://localhost:8080:8080/TestFiles/products.html",
                "http://localhost:8080:8080/TestFiles/about.html",
                "http://localhost:8080:8080/TestFiles/contact.html",
            ],
            "http://localhost:8080/TestFiles/products.html": [
                "http://localhost:8080/TestFiles/index.html",
                "http://localhost:8080/TestFiles/index.html",
                "http://localhost:8080/TestFiles/products.html",
                "http://localhost:8080/TestFiles/about.html",
                "http://localhost:8080/TestFiles/contact.html",
            ],
            "http://localhost:8080/TestFiles/about.html": [
                "http://localhost:8080/TestFiles/index.html",
                "http://localhost:8080/TestFiles/index.html",
                "http://localhost:8080/TestFiles/products.html",
                "http://localhost:8080/TestFiles/about.html",
                "http://localhost:8080/TestFiles/contact.html",
            ],
        }

        with self.assertRaises(SystemExit):
            self.crawl.start_crawler(self.TEST_URL)

            try:
                with open("crawler.log", "r") as file:
                    logs = file.readlines()
            except FileNotFoundError as error:
                assert str(error)

            result_map = collections.defaultdict(list)

            for log in logs:
                if log.startswith("INFO"):
                    link = log.strip().split(": ")[1]

                    if not link.startswith("\t"):
                        key = link
                    else:
                        result_map[key].append(link.strip())

            self.assertDictEqual(dict(result_map), expected_map)


if __name__ == "__main__":
    unittest.main()
