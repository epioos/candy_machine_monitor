import requests


class TlsClient:
    def __init__(self):
        """
        sessions are not possible unless you give the cookies over headers
        """
        self.api_url = "http://49.12.218.232:8082"

    def request(
            self,
            method: str = "GET",  # "GET", "POST", "PUT", "DELETE"
            url: str = "https://ja3er.com/json",  # url
            headers: dict = None,  # default user agent is set to chrome
            json: dict = None,  # {"lang": "de"}
            data: dict = None,  # "body data"
            allow_redirects: bool = True,  # True | False
            timeout: float = 10,  # float seconds
            proxy: str = None,  # http://username:password@ip:port
    ) -> requests.Response:
        """
        :param method:
        :param url:
        :param headers:
        :param json:
        :param data:
        :param allow_redirects:
        :param timeout:
        :param proxy:
        :return:
        """
        if headers is None:
            headers = {}
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                                    "AppleWebKit/537.36 (KHTML, like Gecko) " \
                                    "Chrome/80.0.3987.149 Safari/537.36"
        if proxy is not None:
            headers["Poptls-Proxy"] = proxy
        else:
            headers["Poptls-Proxy"] = ""
        headers["Poptls-Url"] = url
        headers["Poptls-Allowredirect"] = str(allow_redirects).lower()
        headers["Poptls-Timeout"] = str(timeout)
        response = requests.request(
            method=method,
            url=self.api_url,
            timeout=timeout,
            headers=headers,
            json=json,
            data=data,
            verify=False
        )
        return response
