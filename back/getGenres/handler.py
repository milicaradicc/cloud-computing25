import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("MusicStreamingApp")

def lambda_handler(event, context):
    try:

        response = table.scan(
            ProjectionExpression="genres" 
        )

        items = response.get('Items', [])
        all_genres = set()

        for item in items:
            genres_list = item.get('genres', [])
            for genre in genres_list:
                all_genres.add(genre)
        
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
        error_trace = traceback.format_exc()
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"error": str(e), "trace": error_trace})
        }