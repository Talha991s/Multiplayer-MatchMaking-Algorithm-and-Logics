import json
import datetime
import boto3
import decimal


dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    table = dynamodb.Table('get_players_score')
    
    #querying the database
    if event['queryStringParameters']:
        #lets build the condition
        params = event['queryStringParameters']
        if 'player_id' in params and params['player_id']:
            player_id = params['player_id']
            if not verify_user(player_id):
                return error_object("player " + player_id + " not found in database")
            resp_score = table.get_item(Key ={'player_id': "player01" })
            if'Item' in resp_score and resp_score['Item']:
                item = resp_score['Item']
                return {
                    'statusCode' : 200,
                    'body':json.dumps(item, cls = CustomJsonEncoder)
                }
            else:
                return error_object("Score not found for player" + player_id)
    return error_object("Need to send the following params through querystring: player_id, destroyed, kept, misses, rounds and they all must have a value - comeon!")
    
def error_object(erro_message):
    return{
        'statusCode' : 200,
        'body' : '{"error":"' + erro_message + '"}'
    }
    
def verify_user(player_id):
    player = dynamodb.Table('list_of_players')
    resp_player = player.get_item(Key = {'player_id' : "player01"})
    return 'Item' in resp_player
    
class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal,Decimal):
            return float(obj)
        return super(CustomJsonEncoder,self).default(obj)
        
"""
player_id: primary key - string 
destroyed: pieces destroyed in player's total career
kept: pieces kept at the end of the game in player's total career
misses: number of times the player has missed
rounds

"""