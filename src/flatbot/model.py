class Site:
    def __init__(self, url):
        self.url = url

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return not self == other


class Advertisement:
    def __init__(self, url, site):
        self.url = url  # TODO: UUID?
        self.site = site
