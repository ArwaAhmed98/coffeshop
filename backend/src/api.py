import os
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,authorization,True')
    response.headers.add('Access-Control-Allow-Methods' , 'GET,POST,PATCH,DELETE,OPTIONS')
    return response
'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])

def get_drinks():
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True, 
        "drinks": drinks
    }),200
    

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    try:
        drinks = Drink.query.all()
        if drinks is None:
            abort(404)
        drinkss = [drink.long() for drink in drinks]
        return jsonify({
            "success": True, 
            "drinks": drinkss
        }),200
    except:
        abort(422)
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks' ,methods=['POST'])
@requires_auth('post:drinks')
def post_drink(token):
    try:
        # Get Drink  from the POST body
        body = request.get_json()
        if body is None:
            abort(422) #Unprocessable Entity
        #requested_id = body.get('id')
        requested_title = body.get('title')
        requested_recipe = body.get('recipe')
        # Get the response data
        drink = Drink(
            title=requested_title,
            recipe=json.dumps(requested_recipe))
            # dumps => Convert a Python Object into a JSON String)
        drink.insert()
    # Return error if item not added

    #drink  =  Drink.query.filter(id==Drink.id).first() #fetch the last record in the table that I added it with POST   
        return jsonify({
        "success": True, 
        "drinks": [drink.long()]
        }),200
    except:
        abort(AuthError)
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
@app.route('/drinks/<int:id>' , methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token,id):
    try:
        # Get Drink  from the POST body
        body = request.get_json()
        # requested_id = body.get('id')
        requested_title = body.get('title')
        requested_recipe = body.get('recipe')
        to_be_updated_row=Drink.query.filter(Drink.id==id).one_or_none() #See if we have that id is in our Table ?
        if  to_be_updated_row  is None:
            abort(404) #id   is Not found , we do not have that record in our table
        if ( requested_title or  requested_recipe ) is None:
            abort(400) # Wrong Input
        
        to_be_updated_row.title = requested_title
        to_be_updated_row.recipe = json.dumps(requested_recipe)
        try:
            to_be_updated_row.update() # DO the update in the database
        except:
            abort(422) #Unprocessable operation
        #drink = Drink.query.filter_by(Drink.id==id).first() #the last record in the database which is updated in order to get printed 

        return jsonify ({
            "success": True,
            "drinks": [to_be_updated_row.long()]
        }),200

    except:
        abort(422) #Unprocessable Entity
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>' , methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token , id):
    try:
        x=Drink.query.filter(id==Drink.id).one_or_none() #See if we have that is in our Table ?
        if x is None:
            abort(404) # the table does not contain that ordered id
        try:
            x.delete()
        except:
            abort(422) #Unprocessable
            '''
            400 => response status code indicates that the server cannot or will not process
             the request due to something that is perceived to be a client error
              (e.g., malformed request syntax, invalid request message framing,
               or deceptive request routing.
            '''
        return jsonify({
            "success": True,
             "delete": id

        }),200
    except:
        abort(AuthError)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def not_found(error):  
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404


@app.errorhandler(401)
def Unauthorized(error):  
    return jsonify({
        "success": False, 
        "error": 401,
        "message": "Unauthorized"
        }), 401


@app.errorhandler(500)
def server_error(error):  
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal Server Error"
        }), 500




'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    """
    Receive the raised authorization error and propagates it as response
    """
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return jsonify({
        "sucess":False,
        "error":response.status_code,
        "message" :response
       
    }),response.status_code




