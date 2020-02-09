class Site:
    def __init__(self, url, ads):
        self.url = url
        self.ads = ads

    def __bool__(self):
        return bool(self.url)

    def __len__(self):
        return len(self.ads)

    def __eq__(self, other):
        if isinstance(other, Site):
            url_eq = self.url == other.url
            ads_eq = self.ads == other.ads
            return url_eq and ads_eq
        return False

    def __str__(self):
        ads_str = '\n\t'.join(map(str, self.ads))
        return '{}:\n\t{}'.format(self.url, ads_str)


class Advertisement:
    def __init__(self, url, content):
        self.url = url
        self.content = content

    def __key(self):
        return self.url, self.content

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Advertisement):
            return self.__key() == other.__key()
        return NotImplemented

    def __str__(self):
        return '{}: {}'.format(self.url, self.content)
