from urllib.parse import urlparse
from urllib.request import url2pathname


class LocalFileRead():
    """Protocol Adapter to allow Requests to GET file:// URLs"""
    def get_local_file(self, url):
        with open(url) as f:
            print(f.read())


lfa = LocalFileAdapter()
lfa.local_get(r'C:\Users\prath\Downloads\Rescale_Crawler_Ishan.py')