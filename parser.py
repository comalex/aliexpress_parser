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

import sqlite3

from browser import Browser
from detail_page import AliexpressPageParser
from list_parser import ListParser
import config
from config import logger
import db


if __name__ == "__main__":
    # -p "https://www.aliexpress.com/category/200084017/mobile-phone-accessories.html?spm=2114.search0103.8.120.AcjQWq&site=glo&tc=af " -d
    #       https://ru.aliexpress.com/category/202040726/mobile-phone-accessories/2.html?site=rus&tc=af&tag=
    # "https://sale.aliexpress.com/__pc/hot-products.htm?spm=a2g01.8005315.0.0.UJlA8r#"
    parser = argparse.ArgumentParser(description='Aliexpress parser')
    parser.add_argument('-p', '--product_url', help='Aliexpress product list', required=True)
    parser.add_argument('-l', '--limit', help='Limit how many parse links', default=30, type=int)
    parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
    parser.add_argument('-dp', '--debug_proxy', help='Use debug proxy(charles, fiddler)', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', dest='level',
                        default=3, help='Verbose logging (repeat for more verbose)')
    parser.add_argument('-q', '--quiet', action='store_const', const=0, dest='level',
                        default=2, help='Only log errors')
    args = parser.parse_args()

    debug = args.debug
    debug_proxy = args.debug_proxy

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]

    logger.handlers[0].setLevel(levels[min(args.level, len(levels)-1)]) # set level for console handler

    if debug:
        logger.info("DEBUG MODE")
        try:
            os.remove(config.SQLITE_DB)
            logger.info("old db removed")
        except OSError:
            pass
    try:
        db.init()
    except sqlite3.OperationalError:
        pass

    products_list_url = args.product_url
    limit = args.limit

    browser = Browser(debug=debug, use_debug_proxy=debug_proxy)
    url_parser = ListParser(browser, page_count=2)
    for url in url_parser.parse(products_list_url)[:limit]:
        parser = AliexpressPageParser(
            browser, url, max_comments=10, max_transactions=10)
        product = parser.run()

        #save to db
        product_id = db.Product.save(product)
        db.Comments.save(product.get('comments'), product_id)
        db.Transactions.save(product.get('transaction'), product_id)

