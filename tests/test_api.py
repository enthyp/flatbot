import requests


def test_login():
    data = {'login': 'kuba', 'password': 'haslo'}
    req = requests.post('https://192.168.100.106:8443/login', data=data, verify='./ssl/cert.pem')
    print(req.text)
