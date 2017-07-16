import os

from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse


class BS_P(BS):
    """
      Path BeautifulSoup to not pass each time features='lxml'
    """
    def __init__(self, *args, **kwargs):
        if 'features' not in kwargs:
            kwargs['features'] = 'lxml'
        super().__init__(*args, **kwargs)

BeautifulSoup = BS_P


def fix_url(url):
    if not url.startswith("http"):
        url = "https:" + url
    return url


def get_product_id_from_url(url):
    return os.path.splitext(os.path.basename(urlparse(url).path))[0]


def origin_image(url):
    pattern = ".jpg_"
    pos = url.find(pattern)
    if pos != -1:
        url = url[:pos+len(pattern)-1]
    return url

data = {}

def get_db():
    return data

def save_param(product_id, key, val):
    prod = data.setdefault(product_id, {})
    prod[key] = val
