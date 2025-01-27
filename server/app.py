#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Home(Resource):
    def get(self):
        header = "<h1>Code challenge</h1>"
        return make_response(header, 200)

api.add_resource(Home, '/')

class Restaurants(Resource):
    def get(self):
        restaurants = [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
            }
            for restaurant in Restaurant.query.all()
        ]
        return make_response(jsonify(restaurants), 200)


api.add_resource(Restaurants, '/restaurants')
    
class RestaurantInfo(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return make_response(jsonify(restaurant.to_dict()), 200)
        return make_response({"error": "Restaurant not found"}, 404)

    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response({"message": "Restaurant deleted successfully"}, 200)
        return make_response({"error": "Restaurant not found"}, 404)


api.add_resource(RestaurantInfo, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        # Construct response explicitly
        pizzas = [
            {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients,
            }
            for pizza in Pizza.query.all()
        ]
        return make_response(jsonify(pizzas), 200)


api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        # Extract fields from the JSON body
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        # Validate the fields
        if price is None or not (1 <= price <= 30):
            return {"errors": ["Price must be between 1 and 30."]}, 400

        if not pizza_id or not restaurant_id:
            return {"errors": ["Pizza ID and Restaurant ID are required."]}, 400

        # Validate the existence of the pizza and restaurant
        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza:
            return {"errors": ["Invalid Pizza ID."]}, 400
        if not restaurant:
            return {"errors": ["Invalid Restaurant ID."]}, 400

        # Create the RestaurantPizza
        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        # Construct the response with nested data
        response = {
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients,
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
            },
        }

        return make_response(jsonify(response), 201)


api.add_resource(RestaurantPizzas, '/restaurant_pizzas')



if __name__ == "__main__":
    app.run(port=5555, debug=True)
