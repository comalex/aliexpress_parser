"""
Hi, I need a program that could scrape aliexpress product details listing based on specific search url and then saved into database.
 Example of url is :  https://sale.aliexpress.com/__pc/hot-products.htm?spm=a2g01.8005315.0.0.UJlA8r#
 It is a list of hot products in aliexpres. I want some or all of the product details listed from that url result.
  The data should contains product name, price, spesification, detail information if any (the text part in product details tab),
  the images's part, products rate, shop rate, shipping method, current orders and also product reviews and transactions history
  from now to 6 months back. All the data can be scraped inside the product detail. The database should be sqlLite or microsoft excel file.
  The program must be written using python 3 and beautifulsoup/lxml. Anyone that can program python could apply.
   The how to install the program/script should be prepared(dependency things if any, kind of readme doc), so I can run the program properly.
    less

    Because if using sqlite then you have to make at least 2 tables
    1 table for product, and second for comments
"""
import os
import re
import logging
import json
import argparse

from browser import Browser
from detail_page import AliexpressPageParser
from utils import BeautifulSoup, fix_url, get_db
import config
import db

logger = logging.getLogger(__name__)


def parse_products(url, browser):
    res = browser.get(fix_url(url))
    html_text = res.text
    soup = BeautifulSoup(html_text)

    var = soup(text=re.compile(r'data_widgety5zzyn'))

    json_data = json.loads(var[0][var[0].index('{'):])
    products_url = json_data["source"]["url"]

    res = browser.get(fix_url(products_url))
    res.text.lstrip("onJSONPCallback(").rstrip(")")
    json_data = json.loads(res.text.lstrip("onJSONPCallback(").rstrip(");"))
    nodeList = json_data['content']['nodeList'][0]
    name = nodeList['name']
    return nodeList['nodeData']['dataList']


if __name__ == "__main__":
    # "https://sale.aliexpress.com/__pc/hot-products.htm?spm=a2g01.8005315.0.0.UJlA8r#"
    parser = argparse.ArgumentParser(description='Aliexpress parser')
    parser.add_argument('-p', '--product_url', help='Aliexpress product list', required=True)
    parser.add_argument('-l', '--limit', help='Limit how many parse links', default=30, type=int)
    parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
    parser.add_argument('-dp', '--debug_proxy', help='Use debug proxy(charles, fiddler)', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', dest='level',
                        default=2, help='Verbose logging (repeat for more verbose)')
    args = parser.parse_args()

    debug = args.debug
    debug_proxy = args.debug_proxy

    if debug:
        logger.info("DEBUG MODE")
        try:
            os.remove(config.SQLITE_DB)
            logger.info("Old db removed")
        except OSError:
            pass

    db.init()

    products_list_url = args.product_url
    limit = args.limit

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]

    logging.basicConfig(
        format='%(levelname)s - [%(asctime)s] - %(filename)s %(funcName)s():%(lineno)s  - %(message)s',
        level=levels[min(args.level, len(levels)-1)])

    browser = Browser(debug=debug_proxy)

    for prod_data in parse_products(products_list_url, browser)[:limit]:
        parser = AliexpressPageParser(
            browser, prod_data['id'], prod_data['detailUrl'], max_comments=10, max_transactions=10)
        product = parser.run()

        #save to db
        product_id = db.Product.save(product)
        db.Comments.save(product.get('comments'), product_id)
        db.Transactions.save(product.get('transaction'), product_id)

