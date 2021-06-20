from decouple import config

DB_CONTAINER_NAME = config('ETL_DB_CONTAINER_NAME')
DB_PORT = config('ETL_DB_PORT')
DB_CONNECTION_STRING = f'mongodb://{DB_CONTAINER_NAME}:{DB_PORT}'
DB_NAME = config('ETL_DB_NAME')
