import requests
import jwt


class AuthClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def login(self, email, password):
        url = f"{self.base_url}/auth/login"
        params = {'email': email, 'password': password}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get('token')
        else:
            return None
