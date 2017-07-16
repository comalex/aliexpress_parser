import re
from config import logger
from utils import fix_url, origin_image, get_product_id_from_url, BeautifulSoup as BS


class AliexpressPageParser:

    def __init__(self, browser, detail_url, max_comments=100, max_transactions=100):
        self.browser = browser
        self.max_comments = max_comments
        self.max_transactions = max_transactions
        self.product_id = get_product_id_from_url(detail_url)
        self.detail_url = detail_url
        res = browser.get(fix_url(detail_url))
        self.main_page_soap = BS(res.text)
        self.item = {}

    def run(self):
        """
          Call methods which has parse_ prefix
          Position is important !!!
        """
        methods = [getattr(self, m) for m in dir(self) if m.startswith("parse_")]
        for method in methods:
            try:
                method()
            except Exception as e:
                logger.exception(e)
        
        return self.item
    
    def save_param(self, key, value):
        self.item[key] = value

    def get_data(self, tag, attrs, val_type="str"):
        """
        Get values from main page
        :param tag: String
            Example: "h2"
        :param attrs: Dict
            {"class": "class_name"}
        :return String
        """
        text = ""
        try:
            text = self.main_page_soap.find(tag, attrs).text
            if val_type != "str":
                m = re.search(r"[-+]?\d*\.\d+|\d+", text)
                if m:
                    text = m.group()
        except Exception as e:
            logger.debug("PASS: tag: %s, attrs: %s", tag, attrs)
        return text


    def parse_commond_data(self):
        self.save_param('detailUrl', self.detail_url)
        self.save_param('ali_id', self.product_id)
        self.save_param('title', self.get_data("h1", {"class": "product-name"}))
        self.save_param('avgStar', self.get_data("span", {"class": "percent-num"}))
        self.save_param('discount', self.get_data("span", {"class": "p-discount-rate"}))
        self.save_param('minPrice', self.get_data("span", {"id": "j-sku-price"}))
        self.save_param('minMobPromPrice', self.get_data("span", {"id": "j-sku-discount-price"}))
        self.save_param('promLeft', self.get_data("span", {"class": "p-eventtime-left"}))
        self.save_param('orderNum', self.get_data("span", {"id": "j-order-num"}, "int"))
        self.save_param('rantingsNum', self.get_data("span", {"id": "rantings-num"}, "int"))


    def parse_description(self):
        descriptions = []
        for li in self.main_page_soap.find('ul', {'class': 'product-property-list'}).find_all('li'):
            description = {}
            try:
                key, val = li.find_all("span")
                description[key.text.strip(":")] = val.text
                descriptions.append(description)
            except Exception as e:
                logger.exception(e)

        self.save_param('description', descriptions)

    def parse_details(self):
        details_url = fix_url(re.search(r'window.runParams.descUrl="(.*?)";', self.main_page_soap.text).group(1))
        response = self.browser.get(details_url)
        soup = BS(response.text)
        only_text = soup.getText().replace("window.productDescription=", "").strip(" ")
        self.save_param('details', only_text)

    def parse_images(self):
        images = []
        for image in self.main_page_soap.find_all('span', {'class': 'img-thumb-item'}):
            origin_image_path = origin_image(image.img['src'])
            images.append(origin_image_path)

        self.save_param('images', images)

    def parse_feedbacks(self):
        feedback_url = fix_url(self.main_page_soap.find(id="feedback").iframe['thesrc'])
        comments = []
        last_page_count = None
        for page_count in range(1, 10000):
            feedback_r = self.browser.post(feedback_url, {"page": page_count})
            feddback_soap = BS(feedback_r.text)
            if not last_page_count:
                try:
                    a_tags = feddback_soap.find("div", {"class": "ui-pagination-navi util-left"}).find_all("a")
                    last_page_count = int(a_tags[len(a_tags)-2].text)
                except Exception as e:
                    pass
            elif last_page_count < page_count:
                break

            for comment_div in feddback_soap.find_all('div', {'class': 'feedback-item'}):
                try:
                    comment = {}
                    user_data = comment_div.find('div', {'class': 'fb-user-info'})
                    try:
                        user_name = user_data.span.a.text
                    except AttributeError:
                        user_name = user_data.span.text

                    comment['user_name'] = user_name
                    comment['country'] = user_data.b.text
                    comment['comment'] = comment_div.find('dt', {'class': 'buyer-feedback'}).span.text
                    comment['posted_time'] = comment_div.find('dd', {"class": "r-time"}).text

                    start_css = comment_div.find('span', {"class": "star-view"}).span["style"]
                    comment["rating"] = start_css[start_css.find(":"):].strip("%")
                    comments.append(comment)
                except Exception as e:
                    logger.exception(e)

            if self.max_comments < len(comments):
                logger.info("Stopped comments fetching by max_transactions")
                break
        self.save_param('comments', comments)


    def parse_history_transactions(self):
        history_transaction = "https://feedback.aliexpress.com/display/evaluationProductDetailAjaxService.htm?" \
                              "productId=%s&type=default" % self.product_id
        transactions = []
        last_page = None
        for page_count in range(1, 100000):
            transaction_r = self.browser.get(history_transaction, {'page': page_count})
            transaction_json = transaction_r.json()
            if not last_page:
                last_page = int(transaction_json['page']['total'])
            elif last_page < page_count:
                break

            for records in transaction_json['records']:
                transactions.append(records)

            if self.max_transactions < len(transactions):
                logger.info("Stopped transactions fetching by max_transactions")
                break

        self.save_param('transaction', transactions)
