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
    # 使用 http://docs.sqlalchemy.org/en/latest/core/reflection.html
    # 使用检查检查数据库表是否有主键。
    insp = inspect(engine)
    dtype={col_name: NVARCHAR(length=255) for col_name in data.columns.tolist()}
    dtype['id'] = NVARCHAR(length=255)
    print dtype
    data.to_sql(name=table_name, con=engine, if_exists='append', dtype=dtype, index=True, index_label='id')
    # 判断是否存在主键
    if insp.get_primary_keys(table_name) == []:
        with engine.connect() as con:
            # 执行数据库插入数据。
            con.execute('ALTER TABLE `%s` modify (%s) VARCHAR(32);' % (table_name, primary_keys))
            con.execute('ALTER IGNORE TABLE `%s` ADD PRIMARY KEY (%s);' % (table_name, primary_keys))

def init_stocks():
    df = ts.get_stock_basics()
    # df.name = df.name.str.decode("GB2312")
    print [df.name[0]]
    insert_db(df, 'ts_stock_basics', '`id`')

if __name__ == '__main__':
    init_stocks()