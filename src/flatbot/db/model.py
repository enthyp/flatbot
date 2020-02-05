class Site:
    def __init__(self, url, ads):
        self.url = url
        self.ads = ads

    def __eq__(self, other):
        if isinstance(other, Site):
            url_eq = self.url == other.url
            ads_eq = all([
                ad_l == ad_r for ad_l, ad_r in zip(self.ads, other.ads)
            ])
            return url_eq and ads_eq
        return False


class Advertisement:
    def __init__(self, url, content):
        self.url = url
        self.content = content

    def __eq__(self, other):
        if isinstance(other, Advertisement):
            return self.url == other.url and self.content == other.content
        return False
