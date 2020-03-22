from html.parser import HTMLParser


class LinkFinder(HTMLParser):

    def __init__(self, page_url):
        super().__init__()
        self.page_url = page_url
        self.links = set()

    def handle_starttag(self, tag, attributes):
        if tag == 'a':
            for (attr, value) in attributes:
                if attr == 'href':
                    self.links.add(value)

    def page_links(self):
        return self.links
