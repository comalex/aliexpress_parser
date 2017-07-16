import os
import random
import time

import requests

from config import LOG_PATH, logger


class Browser:
    def __init__(self, ua=None, debug=False, use_debug_proxy=False):
        self.session = requests.Session()
        headers = {
            'User-Agent': ua or '5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/603.2.5 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.5',
            'Accept': "text/html,application/xhtml+xml,application/xml;",
            'Accept-Language': 'en-US,en;',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',

        }
        self.session.headers.update(headers)
        self.debug = debug

        if use_debug_proxy:
            self.session.proxies = self.charles_proxy()
            self.session.verify = True

        self.log_folder = os.path.join(LOG_PATH, "html")
        if debug and not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

    def charles_proxy(self):
        """
            For debug: https://www.charlesproxy.com
            Free windows alternative: http://www.telerik.com/fiddler
        """
        charles_proxy = "127.0.0.1:8888"
        return {
            "http": "http://" + charles_proxy,
            "https": "https://" + charles_proxy,
        }

    def save_page(self, res):
        if self.debug:
            try:
                with open(os.path.join(self.log_folder, "page.html"), "w") as f:
                    f.write(str(res.text.encode('utf-8')))
            except Exception as e:
                logger.debug(e)

    def sleep(self, t=None):
        #dummy function for sleep beetween  requests to not be blocked
        time.sleep(t or random.uniform(0.5, 3))

    def _proccess(self, response):
        logger.info("[%s %s]: %s", response.request.method, response.status_code, response.url)
        if response.history:
            logger.debug("[History] %s", response.history)
        self.save_page(response)
        self.sleep()


    def get(self, url, params=None):
        response = self.session.get(url, params=params or {})
        self._proccess(response)
        return response

    def post(self, url, params):
        response = self.session.post(url, data=params)
        self._proccess(response)
        return response