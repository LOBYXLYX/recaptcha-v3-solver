import re
import requests
import base64
import time
import random

class Solver:
    """
    Basic Code:
        solution = Solver(
            '6LfczrUaAAAAAXXXXXXXXXXXXXXXXXXX-XXXX',
            'https://www.example.com'
        )
        token = solution.token()

        print('Solved', solution.solvedTime, 'Token:', token)
    """

    def __init__(
        self, 
        siteKey: str, 
        siteUrl: str,
        userAgent: str = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        grecaptcha_cookie: str = None,
        cb_value: str = 'phia893uehwb',
        proxy: str = None
    ) -> None:
        self.key = siteKey
        self.url = siteUrl
        self.userAgent = userAgent
        self.v = None
        self.hl = 'en'
        self.api = None
        self.grecap_cookie = grecaptcha_cookie
        self.callback_value = cb_value
        self.proxy = proxy

        self.headers: dict[str, str] = None
        self.cookies: requests.cookies = None
        self.anchor_url: str = None
        self._solver_time = time.time()
        self.bg_data = None

        self._get_anchor_info()
        self._google_client()

    def _google_client(self) -> None:
        site = requests.get('https://www.google.com')
        if self.grecap_cookie is not None:
            site.cookies['_GRECAPTCHA'] = self.grecap_cookie
        self.cookies = site.cookies

        self.headers = {
            "accept": "*/*",
            "accept-language": "es-US,es-419;q=0.9,es;q=0.8",
            "content-type": "application/x-protobuffer",
            "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
            "sec-fetch-dest": "empty",
            "origin": "https://www.google.com",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-client-data": "CMTgygE=",
            "user-agent": self.userAgent
        }

    @property
    def solvedTime(self) -> str:
        return self._solver_time

    @property
    def recaptchaApiType(self) -> str:
        parts = self.api.split('/')
        if 'enterprise' in parts:
            return 'Enteprise'
        else:
            return 'Api2'

    def _proxy_support(self) -> dict:
        if self.proxy:
            return {
                'http': self.proxy,
                'https': self.proxy
            }
        return {}

    def _get_anchor_info(self) -> None:
        site_html = requests.get(self.url).text
        try:
            renderUrl = re.findall(
                r"""['"](https://www\.[^/]+/recaptcha/[^'"]+)['"]""", 
                site_html)[0]
        except IndexError:
            static_v = 'i7X0JrnYWy9Y_5EYdoFM79kV'
            renderUrl = f'https://www.google.com/recaptcha/{static_v}/recaptcha__en.js'
        except Exception as e:
            print('Failed to get anchor info:', e)

        r = requests.get(renderUrl).text
        match = re.search(r"po\.src\s*=\s*'(https://[^\']+)';", r)
        if match:
            self.v = match.group(1).split('/')[5]
            self.api = renderUrl.split('.js')[0]

            api_parts = self.api.split('/')

            if not 'api2' in api_parts and not 'enterprise' in api_parts:
                self.api += '2'
        else:
            self.v = renderUrl.split('/')[5]
            self.api = 'https://www.google.com/recaptcha/api2'

    def _co_string(self) -> str:
        if len(self.url.split('/')) > 2:
            parts = self.url.split('/')
            self.url = 'https://' + parts[2]

        url_port = self.url + ':443'

        string_bytes = base64.b64encode(url_port.encode('utf-8'))
        co = string_bytes.decode('utf-8').replace('=', '.') 
        return co

    def _reload_params(self, reCaptchaToken) -> dict[str, str]:
        return {
            'v': self.v,
            'co': self._co_string(),
            'reason': 'q',
            'size': 'invisible',
            'hl': self.hl,
            'k': self.key,
            'c': reCaptchaToken,
            'chr': '%5B61%2C36%2C84%5D',
            'vh': '13599012192',
            'bg': ''
        }

    def _get_recaptcha_token(self) -> str:
        anchor_params = {
            'ar': '1',
            'k': self.key,
            'co': self._co_string(),
            'hl': self.hl,
            'v': self.v,
            'sa': 'action',
            'size': 'invisible',
            'cb': self.callback_value
        }

        self.headers['referer'] = self.url + '/'

        anchor = requests.get(
            f'{self.api}/anchor',
            params=anchor_params,
            cookies=self.cookies,
            headers=self.headers,
            proxies=self._proxy_support()
        ).text

        self.anchor_url = self.api + '/anchor'
        for key_name, value in anchor_params.items():
            self.anchor_url += f'&{key_name}={value}'

        self.headers['referer'] = self.anchor_url
        return anchor.split('recaptcha-token" value="')[1].split('">')[0]

    def token(self) -> str:
        recaptcha_token = self._get_recaptcha_token()
        del self.headers['content-type']

        reload = requests.post(
            f'{self.api}/reload?k={self.key}',
            data=self._reload_params(recaptcha_token),
            cookies=self.cookies,
            headers=self.headers,
            proxies=self._proxy_support()
        ).text

        rresp_token = reload.split('"rresp","')[1].split('"')[0]
        self._solver_time = format(time.time() - self._solver_time, '.3f')
        return rresp_token
