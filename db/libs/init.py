# coding=utf-8
import pandas as pd
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
    return create_engine(DB_CONN_URI_DEFAULT, encoding='utf-8', echo=False, convert_unicode=True)

#定义通用方法函数，插入数据库表，并创建数据库主键，保证重跑数据的时候索引唯一。
def insert_db(data, table_name, primary_keys):
    engine = init_engine()
    data.to_sql(table_name, con=engine, if_exists='append',dtype={'code': NVARCHAR(16), 'date': NVARCHAR(16)})

def init_stock_basics():
    df = ts.get_stock_basics()
    insert_db(df, 'ts_stock_basics', '`id`')

def init_stock_days():
    failed = []
    table_name = 'ts_stock_days'
    # stock_days_df = ts.get_hist_data()
    engine = init_engine()
    sql = 'select code from ts_stock_basics;'
    df = pd.read_sql(sql, con=engine)
    # df.apply(insert_db(table_name))
    for code_tuple in df.code.iteritems():
        code = code_tuple[1]
        stock_days_df = ts.get_hist_data(code)
        if stock_days_df is None:
            failed.append(code)
            print 'Insert', code, 'days data failed ..'
            continue
        stock_days_df['code'] = pd.Series(code, index=stock_days_df.index)
        insert_db(stock_days_df, table_name, '`id`')
        print 'Insert', code, 'days data success ..'
    else:
        print failed

if __name__ == '__main__':
    # init_stock_basics()
    init_stock_days()