import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200
    except:
        abort(404)
  

@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drink_detail(token):
    try:
        drinks_detail = Drink.query.all()
        
        return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks_detail]
    }), 200
    
    except:
        abort(404)    


@app.route("/drinks" , methods=['POST'])
@requires_auth('post:drinks')
def create_drink(token):
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)
    
    try:
        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except:
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, id):
    try:
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        drink.title = body.get('title')

        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200        
    except:
        abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink:
            drink.delete()
            return jsonify({
                'success': True,
                'delete': id
            }), 200
        else:
            abort(404)
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'Error': 404,
        'message': 'resource not found'
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

#error handler for AuthError
@app.errorhandler(AuthError)
def auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        'message': ex.error
    }), 401
