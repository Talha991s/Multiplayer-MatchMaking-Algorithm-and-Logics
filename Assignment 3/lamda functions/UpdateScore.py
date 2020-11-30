import json
import datetime
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    table = dynamodb.Table('get_player_score')
    #querying the database
    if event['queryStringParameters']:
        #build condition
        params = event['queryStringParameters']
        if 'player_id' in params and 'destroyed' in params and 'kept' in params and 'misses' in params and 'rounds' in params and params['player_id'] and params['destroyed'] and params['kept'] and  params['misses'] and params['rounds']:
            player_id = params['player_id']
            if not verify_user(player_id):
                return error_object("player "+ player_id + " not found on database")
            destroyed = int(params['destroyed'])
            kept = int(params['kept'])
            misses = int(params['misses'])
            rounds = int(params['rounds'])
            resp_score = table.get_item(Key={'player_id':player_id})
            if 'Item' in resp_score and resp_score['Item']:
                #update the values
                
                if 'destroyed' in current_score and current_score['destroyed']:
                    current_score['destroyed'] += destroyed
                    
                else:
                    current_score['destroyed'] = destroyed
                    
                    
                if 'kept' in current_score and current_score['kept']:
                    current_score['kept'] += kept
                else:
                    current_score['kept'] = kept
                    
                if ' misses' in current_score and current_score['misses']:
                    current_score['misses']+=misses
                else:
                    current_score['misses'] = misses
                    
                if 'rounds' in current_score and current_score['rounds']:
                    current_score['rounds'] += rounds
                else:
                    current_score['rounds'] = rounds
                    
                table.update_item(
                    Key ={
                        'player_id' :player_id
                    },
                    UpdateExpression = 'SET destroyed = :destroyed, kept = :kept, misses = :misses, rounds = :rounds',
                    ExpressionAttributeValues={
                        ':destroyed': current_score['destroyed'],
                        ':kept': current_score['kept'],
                        ':misses': current_score['misses'],
                        ':rounds': current_score['rounds']
                    }
                )
                
            else:
                new_entry = {
                    'player_id' : player_id,
                    'destroyed' : destroyed,
                    'kept' : kept,
                    'misses' : misses,
                    'rounds' : rounds
                }
                table.put_item(
                    Item = new_entry
                    
                )
                
            return {
                'statusCode': 200,
                'body': '{"result":"Update successful"}'
            }
    return error_object("Need to send the following params through querystring: player_id, destroyed, kept, misses, rounds and they all must have a value - comeon!")
    
    
def error_object(error_message):
    return{
        'statusCode':200,
        'body': '{"result":"Update successful"}'
    }
    
def verify_user(player_id):
    player = dynamodb.Table('list_of_players')
    resp_player = player.get_item(Key ={'player_id': player_id})
    return 'Item' in resp_player
    
class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(CustomJsonEncoder,self).default(obj)
    

"""
player_id: primary key - string 
destroyed: pieces destroyed in player's total career
kept: pieces kept at the end of the game in player's total career
misses: number of times the player has missed
rounds

"""
