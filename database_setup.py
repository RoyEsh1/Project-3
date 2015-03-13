import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Creating Restaurant Table
class Restaurant(Base):
	__tablename__ = 'restaurant'

	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key= True)


	#Crateing serialized property to be used for JSON routing
	@property
	def serialize(self):
	    return {
	    	'name' : self.name,
	    	'id' : self.id,
	    }

# Menu Items Table
class MenuItem(Base):
	__tablename__ = 'menu_item'

	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	course = Column(String(250))
	description = Column(String(250))
	price = Column(String(8))
	restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
	restaurant = relationship(Restaurant)

	#Crateing serialized property to be used for JSON routing
	@property
	def serialize(self):
	    return {
	    	'name' : self.name,
	    	'description' : self.description,
	    	'id' : self.id,
	    	'price' : self.price,
	    	'course' : self.course,
	    }
	
##### END OF FILE ####

engine = create_engine('sqlite:///restaurants.db')

Base.metadata.create_all(engine)