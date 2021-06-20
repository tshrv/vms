from loguru import logger
from pymongo import MongoClient
from src import settings


class DBClient:
    def __init__(self):
        self.client = MongoClient(settings.DB_CONNECTION_STRING)
        self.db = self.client[settings.DB_NAME]
        self.centers = self.db['centers']
        self.sessions = self.db['sessions']
        self.fees = self.db['fees']
        logger.info(f'db client initialized for  {settings.DB_CONNECTION_STRING}')

