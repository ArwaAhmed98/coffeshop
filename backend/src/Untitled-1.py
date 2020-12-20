@app.route('/drinks', methods=['GET'])

def get_drinks():
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True, 
        "drinks": drinks
    }),200
    
    
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    try:
        drinks = Drink.query.all()
        if drinks is None:
            abort(404)
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            "success": True, 
            "drinks": drinks
        }),200
    except:
        abort(422)
        
        
        
        
        
@app.route('/drinks' ,methods=['POST'])
@requires_auth('post:drinks')
def post_drink(token):
    # Get Drink  from the POST body
    body = request.get_json()
    
    requested_id = body.get('id')
    requested_title = body.get('title')
    requested_recipe = body.get('recipe')
    # Get the response data
    drink = Drink(id=requested_id,
            title=requested_title,
            recipe=json.dumps(requested_recipe) # dumps => Convert a Python Object into a JSON String
            )
    drink.insert()
    # Return error if item not added
    if body is None:
        abort(422) #Unprocessable Entity
    #drink  =  Drink.query.order_by(id==Drink.id).first() #fetch the last record in the table that I added it with POST   
    return jsonify({
        "success": True, 
        "drinks": [drink.long()]
    }),200












@app.route('/drinks/<int:id>' , methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token , id):
  try:
        x=Drink.query.filter_by(id==Drink.id).one_or_none() #See if we have that is in our Table ?
        if x is None:
            abort(404)
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
        return({
            "success": True,
             "delete": id

        }),200
    except:
        abort(422)
        
    