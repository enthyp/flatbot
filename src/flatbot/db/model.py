class Site:
    def __init__(self, url, ads):
        self.url = url
        self.ads = ads

    def __eq__(self, other):
        url_eq = self.url == other.url
        ads_eq = all([
            ad_l == ad_r for ad_l, ad_r in zip(self.ads, other.ads)
        ])
        return url_eq and ads_eq

    def __ne__(self, other):
        return not self == other


class Advertisement:
    def __init__(self, url, content):
        self.url = url
        self.content = content

    def __eq__(self, other):
        return self.url == other.url and self.content == other.content

    def __ne__(self, other):
        return not self == other
