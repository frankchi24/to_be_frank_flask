from sqlalchemy import Table, Column, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
# Create an instance of the declarative_base.


class Cookie(Base): # “Inherit from the Base.”
    __tablename__ = 'cookies' #“Define the table name.” 

    cookie_id = Column(Integer(), primary_key=True) 
    cookie_name = Column(String(50), index=True)
    cookie_recipe_url = Column(String(255))
    cookie_sku = Column(String(55))
    quantity = Column(Integer())
    unit_cost = Column(Numeric(12, 2))
    