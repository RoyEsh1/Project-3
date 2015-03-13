from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

#database setup
import sys
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurants.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#-------------------Help Functions

#Creating a function to extract the Restuarant from the URL and returns it. Returns 0 if no resturant was found
def findRestaurant(url):
	# Using Regular Expressions to extract the restaurant ID from the topic
	match = re.search(r'(restaurant_id=)(\d+)' ,url)
	if match:
		restaurant_id = match.group(2)
		rest = session.query(Restaurant).filter_by(id = restaurant_id).one()
	else: rest = 0
	return rest

# Creating a function to extract the Menu Item from the URL and returns it. Returns 0 if no resturant was found
def findItem(url):
	# Regular Expressions
	match = re.search(r'(menu_id=)(\d+)' ,url)
	if match: 
		menu_id = match.group(2)
		item = session.query(MenuItem).filter_by(id = menu_id).one()
	else: item = 0
	return item

#-------------------Restaurants Routing

# Landing Page, creating a query to get list of all restaurants
@app.route('/')
def LandingPage():
	rest = session.query(Restaurant).all()
	return render_template('restaurant_data.html', restaurant=rest)

# Creating a new restaurant
@app.route('/new', methods=['GET','POST'])
def newRestaurant():
	if request.method == 'POST':
		newRestaurant = Restaurant(name = request.form['name'])
		session.add(newRestaurant)
		session.commit()
		flash(newRestaurant.name + " has been created!")
		return redirect(url_for('LandingPage'))
	return render_template('newRestaurant.html')

# Editing a Restaurant
@app.route('/edit', methods=['GET','POST'])
def editRestaurant():
	rest = findRestaurant(request.url)
	if request.method == 'POST':
		oldname = rest.name
		rest.name = request.form['name']		
		session.add(rest)
		session.commit()
		flash(oldname + " has been changed to " + rest.name)
		return redirect(url_for('LandingPage'))
	return render_template('editRestaurant.html', restaurant = rest)

# Deleting a Restaurant
@app.route('/del', methods=['GET','POST'])
def delRestaurant():
	rest = findRestaurant(request.url)
	if request.method == 'POST':
		session.delete(rest)
		session.commit()
		flash(rest.name + " has been deleted")
		return redirect(url_for('LandingPage'))
	return render_template('delRestaurant.html', restaurant = rest)

#------------------Menu Items Routing
 
# Restaurant Details Page
@app.route('/menu')
def RestaurantDetails():
	rest = findRestaurant(request.url)
	items = session.query(MenuItem).filter_by(restaurant_id = rest.id)
	return render_template('menus.html', restaurant=rest, items=items)

# Creating a new Menu Item
@app.route('/menu/new', methods=['GET','POST'])
def newMenuItem():
	rest = findRestaurant(request.url)
	if request.method == 'POST':
		# creating new item in the table
		newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], \
			course = request.form['course'], restaurant_id = rest.id)
		session.add(newItem)
		session.commit()
		flash(newItem.name + " has been created!")
		return redirect(url_for('RestaurantDetails', restaurant_id = rest.id))
	return render_template('newMenuItem.html', restaurant = rest)

# Editing a Menu Item
@app.route('/menu/edit', methods=['GET','POST'])
def editMenuItem():
	rest = findRestaurant(request.url)
	item = findItem(request.url)
	if request.method == 'POST':
		# importing user HTML inputs
		item.name = request.form['name']
		item.description = request.form['description']
		item.price = request.form['price']
		item.course = request.form['course']
		session.add(item)
		session.commit()
		flash(item.name + " has been updated!")
		return redirect(url_for('RestaurantDetails', restaurant_id = rest.id))
	return render_template('editMenuItem.html', restaurant = rest, item = item)

# Deleting a Menu Item
@app.route('/menu/del', methods=['GET','POST'])
def delMenuItem():
	rest = findRestaurant(request.url)
	item = findItem(request.url)
	if request.method == 'POST':
		session.delete(item)
		session.commit()
		flash(item.name + " has been deleted.")
		return redirect(url_for('RestaurantDetails', restaurant_id = rest.id))
	return render_template('delMenuItem.html', restaurant = rest, item = item)

#-------------------JSON

# Dumping information to JSON
# Using: change "/JSON" for all restaurants, "/JSON?restaurant_id=x" for all menu items in restaurant id 'x'
# "/JSON?restaurant_id=x&menu_id=y" to get specific menu item in a specific restaurant
@app.route('/JSON')
def restaurantMenuJSON():
	rest = findRestaurant(request.url)
	restaurants = session.query(Restaurant).all()
	item = findItem(request.url)
	# if restaurant exists in the address bar:
	if rest:
		# get all menu items of the restaurant
		items = session.query(MenuItem).filter_by(restaurant_id = rest.id)
		# if item exist in the address bar, JSONify item
		if item: json = jsonify(MenuItem=[item.serialize])
		# if item doesn't exist in the address bar, JSONify all items
		else: json = jsonify(MenuItems=[i.serialize for i in items])
	else:
		# if restaurant doesn't exist in the address bar, JSONify list of restaurants
		json = jsonify(Restaurants=[i.serialize for i in restaurants])
	return json


if __name__ == '__main__':
		app.secret_key = '123'
		app.debug = True
		app.run(host = '0.0.0.0', port = 5000)

