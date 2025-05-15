import pymongo
from pymongo.errors import ConnectionFailure
import logging
import config

logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """اتصال به پایگاه داده MongoDB"""
    try:
        client = pymongo.MongoClient(config.MONGODB_URI)
        # تست اتصال
        client.admin.command('ping')
        logger.info("اتصال به MongoDB با موفقیت برقرار شد")
        return client
    except ConnectionFailure:
        logger.error("اتصال به MongoDB ناموفق بود")
        return None

def get_db():
    """دریافت اشاره‌گر پایگاه داده"""
    client = connect_to_mongodb()
    if client:
        return client[config.DB_NAME]
    return None