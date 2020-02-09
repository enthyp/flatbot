import requests


def main():
    session = requests.Session()
    session.post('https://192.168.100.106:8443/login',
                 data={'login': 'kuba', 'password': 'haslo'},
                 verify=False)
    url = 'https://www.gumtree.pl/s-pokoje-do-wynajecia/krakow/agh+pokoj+do+wynajecia+krakow/v1c9000l3200208q0p1'

    session.post('https://192.168.100.106:8443/track',
                 data={'base_url': url})


if __name__ == '__main__':
    main()
