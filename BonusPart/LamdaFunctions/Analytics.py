import json
import datetime
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    table = dynamodb.Table('Analytics')
    #save entries
    if event['httpMethod'] == 'POST':
        if 'body' in event:
            request_text = event['body']
            body = json.loads(request_text)
            if 'GameName' in body and 'Username' in  body and 'EventName' in body and 'EventData' in body:
                
                if not verify_user(body['Username']):
                    return error_object('User not found: ' + body['Username'])
                
                if not verify_game(body['GameName']):
                    return error_object('Game not found: ' + body['GameName'])
                    
                if not verify_event(body['EventName']):
                    return error_object('Event not found: '+ body['EventName'])
                    
                item = {
                    'EventDate': datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                    'GameName':  body['GameName'],
                    'Username':  body['Username'],
                    'EventName': body['EventName'],
                    'EventData': body['EventData']
                }
                table.put_item(
                    Item = item
                )
                
                return {
                     'statusCode': 200,
                    'body': '{"result": "Event logged successfully"}'
                }
            else:
                #bad request
                return error_object('Bad Request - needs to send GameName, Username, EventName, and EventData in the request body')
        else:
            return error_object('Bad Request - needs to send a request body')
    elif event['httpMethod'] == 'GET':
        #querying the database
        
        if event['queryStringParameters']:
            #condition
            query_request = event['queryStringParameters']
            params = Attr('EventDate').gt('0')
            if 'GameName' in query_request and query_request['GameName'] :
                params = params & Attr('GameName').eq(query_request['GameName'])
            if 'Username' in query_request and query_request['Username'] :
                params = params & Attr('Username').eq(query_request['Username'])
            if 'DateTimeStart' in query_request and query_request['DateTimeStart'] :
                params = params & Attr('EventDate').gte(query_request['DateTimeStart'])
            if 'DateTimeEnd' in query_request and query_request['DateTimeEnd'] :
                params = params & Attr('EventDate').lte(query_request['DateTimeEnd'])
            return {
                'statusCode': 200,
                'body': json.dumps(table.scan(FilterExpression = params), cls = CustomJsonEncoder)
            }
        else:
            #perform a simple table scan
            return{
                'statusCode': 200,
                'body':json.dumps(table.scan(), cls = CustomJsonEncoder)
            }
    else:
        return error_object('Only GET and POST are supported')
        
        
def error_object(error_message):
    return{
         'statusCode': 200,
        'body': '{"error":"' + error_message + '"}' 
    }
    
def verify_user(player_id):
    player = dynamodb.Table('list_of_players')
    resp_player = player.get_item(Key={'player_id':player_id})
    return 'Item' in resp_player
    
def verify_game(game_name):
    game = dynamodb.Table('RemoteSetting')
    resp_game = game.get_item(Key={'GameName':game_name})
    return 'Item' in resp_game
    
def verify_event(event_name):
    event = dynamodb.Table('Event')
    resp_event = event.get_item(Key={'Name':event_name})
    return 'Item' in resp_event
    
class CustomJsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(CustomJsonEncoder, self).default(obj)
            