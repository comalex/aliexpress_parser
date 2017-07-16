import logging
import logging.config
import os
import sys

import time

LOG_PATH = "logs"
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

SQLITE_DB = "ali.db"
SESSION_ID = "%d%d" % (time.time(), os.getpid())

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
    },
    'loggers': {
        'ali_parser': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'ali',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_PATH, SESSION_ID+".txt"),
            'formatter': 'ali',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s: %(message)s',
        },
        'file': {
            'format': '%(message)s',
        },
        'ali': {
            'format': '%(levelname)s - [%(asctime)s] - %(filename)s %(funcName)s():%(lineno)s  - %(message)s'
        },
    },
}


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('ali_parser')