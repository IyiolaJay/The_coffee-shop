import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import UnprocessableEntity
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
# db_drop_and_create_all()

# # ROUTES
# '''
# @TODO implement endpoint
#     GET /drinks
#         it should be a public endpoint
#         it should contain only the drink.short() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    }), 200

# '''
# @TODO implement endpoint
#     GET /drinks-detail
#         it should require the 'get:drinks-detail' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detailed(payload):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    }), 200
# '''
# @TODO implement endpoint
#     POST /drinks
#         it should create a new row in the drinks table
#         it should require the 'post:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()
    
    if not ("title" in body and "recipe" in body):
        abort(400, "Request malformed, requires title and recipes")
    
    title = body.get('title')
    recipe = body.get('recipe')
    
    if type(recipe) is dict:
        recipe = [recipe]
        value = json.dumps(recipe)
    
    else:
        value = json.dumps(recipe)


    try:
        drink = Drink(title=title, recipe=value)
        drink.insert()
        drinks = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200

    except exc.IntegrityError:
        abort(422, "Drink already exists")

# '''
# @TODO implement endpoint
#     PATCH /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should update the corresponding row for <id>
#         it should require the 'patch:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
#         or appropriate status code indicating reason for failure
# '''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.get(id)
    body = request.get_json()
    
    if drink is None:
        abort(404, "Drink does not exist")

    elif body is None:
        abort(400, "Request Malformed: requires drink titles and recipes")
    
    try:
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

        if new_title != None:
            drink.title = new_title
        
        if new_recipe != None:
            if type(new_recipe) is dict:
                new_recipes = [new_recipe]
                value = json.dumps(new_recipes)
        
            else:
                value = json.dumps(new_recipe)

            drink.recipe = value
        
        drink.update()
        drinks = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200

    except:
        abort(401)

# '''
# @TODO implement endpoint
#     DELETE /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should delete the corresponding row for <id>
#         it should require the 'delete:drinks' permission
#     returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
#         or appropriate status code indicating reason for failure
# '''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drink(payload, id):
    drinks = Drink.query.get(id)
    if drinks:
        try:
            drinks.delete()
            return jsonify({
                'success': True,
                'delete': drinks.id
            }), 200
        except:
            abort(422, "Cannot process this delete operation")
    else:
        abort(404, "Drink does not exist")
    
# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": {error}
    }), 422


# '''
# @TODO implement error handlers using the @app.errorhandler(error) decorator
#     each error handler should return (with approprate messages):
#              jsonify({
#                     "success": False,
#                     "error": 404,
#                     "message": "resource not found"
#                     }), 404

# '''
@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": {error}
    }), 400

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": {error}
    }), 404

@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": {error}
    }), 401

@app.errorhandler(403)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": {error}
    }), 403
# '''
# @TODO implement error handler for 404
#     error handler should conform to general task above
# '''


# '''
# @TODO implement error handler for AuthError
#     error handler should conform to general task above
# '''
@app.errorhandler(AuthError)
def auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error
    }), 403

@app.errorhandler(AuthError)
def auth_error_unauthorized(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error
    }), 401