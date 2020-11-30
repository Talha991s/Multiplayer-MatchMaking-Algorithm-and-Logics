import json
import datetime
import boto3
import decimal


dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):
    table = dynamodb.Table("list_of_players")
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(table.scan(), cls = CustomJsonEncoder)
    }
    
class CustomJsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(CustomJsonEncoder, self).default(obj)
