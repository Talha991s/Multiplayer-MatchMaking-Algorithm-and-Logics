import json
import boto3

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    
    table = dynamodb.Table('RemoteSettings')
    # tries to find information about the game
    if event['httpMethod'] == 'GET':
        if 'queryStringParameters' in event:
            params = event['queryStringParameters']
            if 'GameName' in params:
                game_name = params['GameName']
                response = table.get_item(Key = {'GameName':game_name})
                if 'Item' in reponse:
                    item = reponse['Item']
                    return{
                        'statusCode':200,
                        'body':json.dumps(item)
                    }
                else:
                    return error_object('Game not found: '+ game_name)
            else:
                return error_object('Bad Request - need to send GameName in the request querystring parameter')
        else:
            #Bad request
            return error_object('Bad Request - needs to send a request querystring parameter')
    elif event['httpMethod'] == 'POST':
        if 'body' in event:
            request_text = event['body']
            body = json.loads(request_text)
            if 'GameName' in body and 'Key' in body and 'Value' in body:
                game_name = body['GameName']
                response = table.get_item(Key = {'GameName':game_name})
                if 'Item' in  response:
                    game_var = body['Key']
                    game_val = body['Value']
                    table.update_item(
                        Key = {
                            'GameName' : game_name
                        },
                        UpdateExpression = 'SET ' + game_var + ' = :val',
                        ExpressionAttributeValues={
                            ':val':game_val
                        }
                    )
                    return {
                        'statusCode': 200,
                        'body': '{"result": "' + game_name + ' updated '  + game_var + ' successfully"}'
                    }
                else:
                    return error_object('Game not found: ' + game_name)
            else:
                return error_object('Bad Request - needs to send GameName, Key and value in the request body')
        else:
            #BadRequest
            return error_object('Bad Request - needs to send a request body')
    else:
        return error_object('Only GET and POST are supported')
        
        
def error_object(error_message):
    return{
        'statusCode':200,
        'body': '{"error":"' + error_message + '"}' 
    }