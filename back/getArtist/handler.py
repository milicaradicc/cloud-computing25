import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("Artists")

def lambda_handler(event, context):
    try:
        artists = []
        last_evaluated_key = None

        while True:
            if last_evaluated_key:
                response = table.scan(
                    ExclusiveStartKey=last_evaluated_key
                )
            else:
                response = table.scan()

            items = response.get('Items', [])

            # Map DynamoDB items to Artist interface
            for item in items:
                artist = {
                    "id": item.get("Id"),             # sort key
                    "name": item.get("name"),
                    "biography": item.get("biography"),
                    "genres": item.get("genres", []),
                    "genre": item.get("Genre")        # partition key
                }
                artists.append(artist)

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        return {
            'statusCode': 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            'body': json.dumps(artists)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            'body': json.dumps({"error": str(e)})
        }
