import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('ARTISTS_TABLE_NAME', 'Artists')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):

    try:
        all_genres = set()
        
        scan_kwargs = {
            'ProjectionExpression': 'Genre'
        }

        while True:
            response = table.scan(**scan_kwargs)
            items = response.get('Items', [])
            
            for item in items:
                if 'Genre' in item:
                    all_genres.add(item['Genre'])
            
            if 'LastEvaluatedKey' not in response:
                break
            
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*", 
                "Content-Type": "application/json"
            },
            'body': json.dumps(list(all_genres))
        }

    except Exception as e:
        import traceback
        print("Error occurred:", e)
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"error": str(e)})
        }
