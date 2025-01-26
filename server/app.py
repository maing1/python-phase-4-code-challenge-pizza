#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from werkzeug.exceptions import NotFound
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch= True)

db.init_app(app)

api = Api(app)


class Home(Resource):
    def get(self):
        header = "<h1>Code challenge</h1>"
        return make_response(header, 200)

api.add_resource(Home, '/')

class Restaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
        return make_response(jsonify(restaurants), 200)
    
api.add_resource(Restaurants, '/restaurants')

class RestaurantPizza(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            return make_response(restaurant.to_dict(), 200)
        return make_response(
            {"error": f"Restaurant not found"}, 404)
    
    def delete_restaurant(id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response(
                {"message": "User deleted successfully"}, 200
            )
        return make_response(
            {"error": f"Restaurant not found"}, 404
        )

api.add_resource(RestaurantPizza,'/restaurants/<int:id>')

class Pizza(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])
    def post(self):
         # Extract the data directly from the request JSON
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
            "pizza_id": pizza.id,
            "restaurant_id": restaurant.id,
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

api.add_resource(Pizza, '/pizzas')

@app.errorhandler(NotFound)
def handle_not_found(e):
    return make_response(
        "Not Found: The requested resource does not exist.", 404
    )

app.register_error_handler(404, handle_not_found)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
