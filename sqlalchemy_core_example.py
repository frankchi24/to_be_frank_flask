# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, Numeric, String, ForeignKey
from sqlalchemy import Index
from sqlalchemy.sql import select, insert

engine = create_engine('mysql://root:bestdrumer322@localhost/testing?charset=utf8')
connection = engine.connect()
metadata = MetaData()


cookies = Table('cookies', metadata,
    Column('cookie_id', Integer(), primary_key=True), 
    Column('cookie_name', String(50)), 
    Column('cookie_recipe_url', String(255)),
    Column('cookie_sku', String(55)),
    Column('quantity', Integer()),
    Column('unit_cost', Numeric(12, 2)) 
)

material = Table('material',metadata,
	Column('mid',Integer(),primary_key = True),
	Column('test',String(50),index = True)
)

metadata.create_all(engine)

s = cookies.select()
# s = select([cookies])
rp = connection.execute(s)
for r in rp:
	print r
print '--------------------'

new = insert(cookies).values(
	cookie_name = 'chocalate chip',
	cookie_recipe_url = 'www.google.com',
	cookie_sku = 'CC01',
	quantity = '12',
	unit_cost = '22.25'
	)

ne = connection.execute(new)




