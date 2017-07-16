import json
import re
from utils import fix_url, BeautifulSoup
from config import logger


class ListParser:

    def __init__(self, browser, page_count=100):
        self.browser = browser
        self.page_count = page_count

    def parse(self, start_url):
        url_list = []
        methods = [getattr(self, m) for m in dir(self) if m.startswith("parse_")]
        for method in methods:
            try:
                url_list = method(start_url)
            except Exception as e:
                logger.debug("Pass %s", method.__name__)
        return url_list

    def parse_sale_page(self, url):
        res = self.browser.get(fix_url(url))
        html_text = res.text
        soap_page = BeautifulSoup(html_text)
        var = soap_page(text=re.compile(r'data_widgety5zzyn'))
        json_data = json.loads(var[0][var[0].index('{'):])
        products_url = json_data["source"]["url"]
        res = self.browser.get(fix_url(products_url))
        res.text.lstrip("onJSONPCallback(").rstrip(")")
        json_data = json.loads(res.text.lstrip("onJSONPCallback(").rstrip(");"))
        nodeList = json_data['content']['nodeList'][0]
        name = nodeList['name']
        return [item['detailUrl'] for item in nodeList['nodeData']['dataList']]

    def parse_search_page(self, url):
        url_list = []
        for _ in range(self.page_count):
            res = self.browser.get(fix_url(url))
            html_text = res.text
            soap_page = BeautifulSoup(html_text)

            for prod_element in soap_page.find("ul", {"id": re.compile(r"list-items")}).find_all("li"):
                url_list.append(fix_url(prod_element.find("a", {"href": re.compile("aliexpress.com/item")})["href"]))

            try:
                url = soap_page.find("div", {"class": "ui-pagination-navi"}).find("a", {"class": "page-next"}).attrs["href"]
            except Exception as e:
                logger.debug(e)
                break
        return url_list

