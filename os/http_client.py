import requests


class Client:
    def __init__(self, proxy="", timeout=10, ja3=""):
        """
        :param proxy:
        :param timeout:
        :param ja3:
        """
        self.api_url = "http://23.88.50.74:8082"
        self.proxy = proxy  # DEFAULT "" (proxyless) ODER "http://user:pass@host:port"
        self.timeout = timeout
        self.ja3 = ja3

    def rotate_proxy(self, new_proxy: str):
        """
        :param new_proxy:
        :return:
        """
        self.proxy = new_proxy

    def request(
            self,
            url: str,
            headers: dict,
            method: str = "GET",
            allow_redirects=False,
            data: str = "",
    ):
        """
        :param url:
        :param headers:
        :param method:
        :param allow_redirects:
        :param data: kann auch zu json geändert werden
        :return:
        """
        headers["Poptls-Key"] = "SUNSTINKT"  # ohne key kann die api nicht verwendet werden (passwort)
        headers["Poptls-Url"] = url  # die eigentliche url
        headers["Poptls-Proxy"] = self.proxy
        headers["Poptls-ja3"] = self.ja3
        headers["Poptls-Allowredirect"] = allow_redirects.__str__().lower()
        response = requests.request(method, self.api_url, headers=headers, timeout=self.timeout, data=data)
        if response.status_code == 401:
            print("headers", headers)
            print(response.text)
        # print(response.request.headers)
        # print(response.text)
        return response
