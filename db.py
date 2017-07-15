import json
import os
import sqlite3
import config
from config import logger

conn = None
cursor = None

def create_tables():
    PRODUCT = """
        CREATE TABLE `product` (
            `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            `ali_id`	INTEGER NOT NULL UNIQUE,
            `title`	TEXT NOT NULL,
            `minPrice`	TEXT,
            `minMobPromPrice`	TEXT,
            `details`	TEXT,
            `description`	TEXT,
            `detailUrl`	TEXT,
            `pic1`	TEXT DEFAULT 'N/A',
            `pic2`	TEXT DEFAULT 'N/A',
            `pic3`	TEXT DEFAULT 'N/A',
            `pic4`	TEXT DEFAULT 'N/A',
            `pic5`	TEXT DEFAULT 'N/A',
            `pic6`	TEXT DEFAULT 'N/A'
        );    
    """
    cursor.execute(PRODUCT)
    logger.info("Created PRODUCT table")
    COMMENT = """
        CREATE TABLE `comment` (
            `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            `product_id`	INTEGER NOT NULL,
            `user_name`	TEXT,
            `comment`	TEXT,
            `country`	TEXT,
            `rating` INTEGER,
            `posted_time`	TEXT
        ); 
    """
    cursor.execute(COMMENT)
    logger.info("Created COMMENT table")

    TRANSACTION_HISTORY = """
        CREATE TABLE `transaction_history` (
            `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            `product_id`	INTEGER NOT NULL,
            `name`	TEXT,
            `lotNum` INTEGER,
            `countryCode`	TEXT,
            `countryName`	TEXT,
            `quantity`	INTEGER,
            `date`	TEXT,
            `unit`	TEXT
        ); 
    """

    cursor.execute(TRANSACTION_HISTORY)
    logger.info("Created TRANSACTION_HISTORY table")



class Table:
    def __init__(self, table_name):
        self.table_name = table_name.lower()

    def get_fields(self):
        try:
            cursor.execute("SELECT * FROM {}".format(self.table_name))
        except Exception as e:
            import pdb; pdb.set_trace()
        return [description[0] for description in cursor.description]

    def filter_data(self, data):
        fields = self.get_fields()

        exclude = ["id",]
        filtered_data = {}
        for key, value in data.items():
            if key in fields and key not in exclude:
                filtered_data[key] = value
        return filtered_data

    def process_data(self, data):
        return data

    def save(self, data_info, product_id=None):
        for data in data_info if isinstance(data_info, list) else [data_info, ]:
         try:
              if not data:
                  continue

              if product_id:
                  data['product_id'] = product_id

              data = self.filter_data(self.process_data(data))
              values = data.values()
              query = """INSERT INTO {} {} VALUES ({});""".format(self.table_name, tuple(data.keys()), ",".join(["?" for _ in range(len(values))]))
              logger.debug(query)
              cursor.execute(query, tuple(data.values()))
              conn.commit()
         except Exception as e:
           logger.exception(e)

        return cursor.lastrowid


class ProductClass(Table):
    def process_data(self, data):
        images_fields = [f for f in self.get_fields() if f.startswith("pic")]
        images = data['images']
        for field_name, val in zip(images_fields, images):
            data[field_name] = val
        data['description'] = json.dumps(data['description'])
        return data


Product = ProductClass('Product')
Comments = Table('Comment')
Transactions = Table('Transaction_history')


def init():
    global conn, cursor
    conn = sqlite3.connect(config.SQLITE_DB)
    cursor = conn.cursor()
    create_tables()


if __name__ == "__main__":
    logger.info("Init sqllite database")
    try:
        os.remove(config.SQLITE_DB)
        logger.info("Old db removed")
    except OSError:
        pass
    init()
