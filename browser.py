import os

import requests
import logging
from config import LOG_PATH

logger = logging.getLogger(__name__)


class Browser:
    def __init__(self, ua=None, debug=False, use_debug_proxy=False):
        self.session = requests.Session()
        headers = {
            'User-Agent': ua or 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0',
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
            with open(os.path.join(self.log_folder, "page.html"), "w") as f:
                f.write(res.text)

    def get(self, url, params=None):
        response = self.session.get(url, params=params or {})
        logger.info("[GET %s]: %s", response.status_code, url)
        self.save_page(response)
        return response

    def post(self, url, params):
        response = self.session.post(url, data=params)
        logger.info("[POST %s]: %s", response.status_code, url)
        self.save_page(response)
        return response