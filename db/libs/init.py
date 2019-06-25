# coding=utf-8
import tushare as ts
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    inspect
)
from sqlalchemy.pool import NullPool
from sqlalchemy.types import NVARCHAR

DB_CONFIG_DICT = {
        'user': 'root',
        'password': 'lhg03712',
        'host': '159.65.69.28',
        'port': 3306,
}

DEFAULT_DB_NAME = 'stocks_data'
DB_CONN_FORMAT = "mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8"

DB_CONN_URI_DEFAULT = (DB_CONN_FORMAT.format(
    database=DEFAULT_DB_NAME,
    **DB_CONFIG_DICT))

DB_CONN_URI_NEW = (DB_CONN_FORMAT.format(
    database=DEFAULT_DB_NAME,
    **DB_CONFIG_DICT))

def init_engine():
    return create_engine(DB_CONN_URI_DEFAULT, encoding='utf-8', echo=True, convert_unicode=True)

#定义通用方法函数，插入数据库表，并创建数据库主键，保证重跑数据的时候索引唯一。
def insert_db(data, table_name, primary_keys):
    engine = init_engine()
    data.to_sql(table_name, con=engine, if_exists='replace',dtype={'code': NVARCHAR(data.index.get_level_values('code').str.len().max())})

def init_stock_basics():
    df = ts.get_stock_basics()
    insert_db(df, 'ts_stock_basics', '`id`')

def init_stocks_days():
    pass
    
if __name__ == '__main__':
    init_stock_basics()