from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://abdulrahman@localhost:5432/fyyapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


order_items = db.Table('order_items',
                       db.Column('order_id', db.Integer, db.ForeignKey(
                           'sales.id'), primary_key=True),
                       db.Column('product_id', db.Integer, db.ForeignKey(
                           'product.id'), primary_key=True),
                       )


class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(), nullable=False)
    products = db.relationship(
        'Product', secondary=order_items, backref=db.backref('orders', lazy=True))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


if __name__ == '__main__':
    app.run()
