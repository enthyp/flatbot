import requests


def main():
    session = requests.Session()
    session.post('http://0.0.0.0:8443/login',
                 data={'login': 'kuba', 'password': 'haslo'})
    url = 'https://www.gumtree.pl/s-pokoje-do-wynajecia/krakow/agh+pokoj+do+wynajecia+krakow/v1c9000l3200208q0p1'

    session.post('http://0.0.0.0:8443/untrack',
                 data={'base_url': url})


if __name__ == '__main__':
    main()
