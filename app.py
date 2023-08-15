from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'

uri = os.getenv("DATABASE_URL")
if uri:
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///app.db'


jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# models yang digunakan
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    photos_link = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('recipe', lazy=True))

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'photos_link': self.photos_link,
            'user_id': self.user_id
        }

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

# routes yang digunakan
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = generate_password_hash(data.get('password'))

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify(message='User created successfully'), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        token = create_access_token(identity=user.id)
        return jsonify(token=token), 200

    return jsonify(message='Invalid credentials'), 401

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/get_recipe', methods=['GET'])
def recipes():
    recipes = Recipe.query.all()
    return jsonify([recipe.serialize() for recipe in recipes]), 200

@app.route('/add_recipe', methods=['POST'])
@jwt_required()
def add_recipe():
    user_id = get_jwt_identity()
    if user_id is None:
        return jsonify(message='Unauthorized'), 401
    else:
        data = request.json
        title = data.get('title')
        content = data.get('content')
        photos_link = data.get('photos_link')

        recipe = Recipe(title=title, content=content, photos_link=photos_link, user_id=user_id)

        db.session.add(recipe)
        db.session.commit()

        return jsonify(message='Recipe created successfully'), 201

@app.route('/toggle_like/<int:recipe_id>', methods=['POST'])
@jwt_required()
def toggle_like(recipe_id):
    user_id = get_jwt_identity()
    if user_id is None:
        return jsonify(message='Unauthorized'), 401
    else:
        like = Like.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        if like:
            db.session.delete(like)
            db.session.commit()
            return jsonify(message='Like removed'), 200
        else:
            like = Like(user_id=user_id, recipe_id=recipe_id)
            db.session.add(like)
            db.session.commit()
            return jsonify(message='Like added'), 200

@app.route('/check_like/<int:recipe_id>', methods=['GET'])
@jwt_required()
def check_like(recipe_id):
    user_id = get_jwt_identity()
    if user_id is None:
        return jsonify(message='Unauthorized'), 401
    else:
        like = Like.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        if like:
            return jsonify(liked=True), 200
        else:
            return jsonify(liked=False), 200

@app.route('/me', methods=['GET'])
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    if user_id is None:
        return jsonify(message='Unauthorized'), 401
    else:
        user = User.query.get(user_id)
        return jsonify(id=user.id, username=user.username), 200

if __name__ == '__main__':
    app.run(debug=True)
