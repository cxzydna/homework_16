from datetime import datetime

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

import raw_data
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///:memory:'

db = SQLAlchemy(app)


def get_response(data):
    return json.dumps(data), 200, {'Content-Type': 'application/json; charset=utf-8'}




class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String())
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    __tablename__ = 'offer'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.create_all()

    for user_data in raw_data.users:
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()

    for order_data in raw_data.orders:
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%m/%d/%Y').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%m/%d/%Y').date()
        new_order = Order(**order_data)
        db.session.add(new_order)
        db.session.commit()

    for offer_data in raw_data.offers:
        new_offer = Offer(**offer_data)
        db.session.add(new_offer)
        db.session.commit()


@app.route('/users', methods=['GET', 'POST'])
def users_page():
    if request.method == 'GET':
        users = User.query.all()
        res = [user.to_dict() for user in users]
        return get_response(res)
    elif request.method == 'POST':
        usr_data = json.loads(request.data)
        db.session.add(User(**usr_data))
        db.session.commit()
        return '', 201


@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user_page(uid):
    if request.method == 'GET':
        user = User.query.get(uid).to_dict()
        return get_response(user)
    if request.method == 'DELETE':
        user = User.query.get(uid)
        db.session.delete(user)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        usr_data = json.loads(request.data)
        user = User.query.get(uid)
        user.first_name = usr_data['first_name']
        user.last_name = usr_data['last_name']
        user.role = usr_data['role']
        user.phone = usr_data['phone']
        user.email = usr_data['email']
        user.age = usr_data['age']
        return '', 204


@app.route('/orders', methods=['GET', 'POST'])
def orders_page():
    if request.method == 'GET':
        orders = Order.query.all()
        res = []
        for order in orders:
            ord_dict = order.to_dict()
            ord_dict['start_date'] = str(ord_dict['start_date'])
            ord_dict['end_date'] = str(ord_dict['end_date'])
            res.append(ord_dict)
        return get_response(res)
    elif request.method == 'POST':
        ord_data = json.loads(request.data)
        db.session.add(Order(**ord_data))
        db.session.commit()
        return '', 201


@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def order_page(oid):
    order = Order.query.get(oid)
    if request.method == 'GET':
        ord_dict = order.to_dict()
        ord_dict['start_date'] = str(ord_dict['start_date'])
        ord_dict['end_date'] = str(ord_dict['end_date'])
        return get_response(ord_dict)
    if request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        ord_data = json.loads(request.data)
        ord_data['start_date'] = datetime.strptime(ord_data['start_date'], '%Y-%m-%d').date()
        ord_data['end_date'] = datetime.strptime(ord_data['start_date'], '%Y-%m-%d').date()

        order.name = ord_data['name']
        order.description = ord_data['description']
        order.start_date = ord_data['start_date']
        order.end_date = ord_data['end_date']
        order.price = ord_data['price']
        order.customer_id = ord_data['customer_id']
        order.executor_id = ord_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return '', 204


@app.route('/offers', methods=['GET', 'POST'])
def offers_page():
    if request.method == 'GET':
        offers = Offer.query.all()
        res = [offer.to_dict() for offer in offers]
        return get_response(res)
    elif request.method == 'POST':
        ofr_data = json.loads(request.data)
        db.session.add(Offer(**ofr_data))
        db.session.commit()
        return '', 201


@app.route('/offers/<int:ofid>', methods=['GET', 'PUT', 'DELETE'])
def offer_page(ofid):
    if request.method == 'GET':
        offer = Offer.query.get(ofid).to_dict()
        return get_response(offer)
    if request.method == 'DELETE':
        offer = Offer.query.get(ofid)
        db.session.delete(offer)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        ofr_data = json.loads(request.data)
        offer = Offer.query.get(ofid)
        offer.order_id = ofr_data['order_id']
        offer.executor_id = ofr_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
