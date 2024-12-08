#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class RestaurantById(Resource):
    def get(self, id):
        try:
            restaurant = Restaurant.query.get_or_404(id)
            return restaurant.to_dict(), 200
        except Exception as e:
            return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        try:
            restaurant = Restaurant.query.get_or_404(id)
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        except Exception as e:
            return {"errors": str(e)}, 404


api.add_resource(RestaurantById, "/restaurants/<int:id>")

class Restaurants(Resource):
    def get(self):
        try:
            restaurants = Restaurant.query.all()
            return [restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants], 200
        except Exception as e:
            return {"error": str(e)}, 400

api.add_resource(Restaurants, "/restaurants")

class Pizzas(Resource):
    def get(self):
        try:
            pizzas = Pizza.query.all()
            return [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas], 200
        except Exception as e:
            return {"error": str(e)}, 400

api.add_resource(Pizzas, "/pizzas")

class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_restaurant_obj = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(new_restaurant_obj)
            db.session.commit()
            return make_response(new_restaurant_obj.to_dict(), 201)
        except ValueError as e:
            return {"errors": ["validation errors"]}, 400
        except Exception as e:
            return {"errors": str(e)}, 400

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == '__main__':
    app.run(port=5555, debug=True)