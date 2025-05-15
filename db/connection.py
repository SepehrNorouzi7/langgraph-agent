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
    except ConnectionFailure as e:
        logger.error(f"اتصال به MongoDB ناموفق بود: {e}")
        return None
    except Exception as e:
        logger.error(f"خطای پیش‌بینی نشده در اتصال به MongoDB: {e}")
        return None

def get_db():
    """دریافت اشاره‌گر پایگاه داده"""
    client = connect_to_mongodb()
    if client:
        db = client[config.DB_NAME]
        logger.debug(f"پایگاه داده {config.DB_NAME} با موفقیت دریافت شد")
        return db
    logger.error("امکان دریافت پایگاه داده وجود ندارد (اتصال برقرار نیست)")
    return None