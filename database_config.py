from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configure app and instantiate database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cibo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Classes created following the model given in the Flask SQLAlchemy 
# documentation at https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hash = db.Column(db.String(80), unique=False, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date)
    description = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80))
    serving = db.Column(db.Integer)
    calories = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    fat = db.Column(db.Integer)

    def __repr__(self):
        return f"{{'date': '{self.date}', 'description': '{self.description}', 'brand': '{self.brand}', 'serving': '{self.serving}', 'calories': {self.calories}, 'carbs': {self.carbs}, 'protein': {self.protein}, 'fat': {self.fat} }}"


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80))
    calories = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    fat = db.Column(db.Integer)

    def __repr__(self):
        return f"{{'description': '{self.description}', 'brand': '{self.brand}', 'calories': {self.calories}, 'carbs': {self.carbs}, 'protein': {self.protein}, 'fat': {self.fat} }}"


# Configure database
db.create_all()