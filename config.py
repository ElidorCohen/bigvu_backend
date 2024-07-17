import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    MEANING_CLOUD_KEY = os.getenv('MEANING_CLOUD_API_KEY')
    DEBUG = True


config = Config()
