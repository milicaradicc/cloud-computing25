import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("MusicStreamingApp")


def lambda_handler(event, context):
    try:
        artists = []
        last_evaluated_key = None

        while True:
            if last_evaluated_key:
                response = table.query(
                    IndexName="entityType-index",
                    KeyConditionExpression=Key('entityType').eq('artist'),
                    ExclusiveStartKey=last_evaluated_key
                )
            else:
                response = table.query(
                    IndexName="entityType-index",
                    KeyConditionExpression=Key('entityType').eq('artist')
                )

            items = response.get('Items', [])

            # Map DynamoDB items to Artist interface
            for item in items:
                artist = {
                    "id": item.get("artistId"),
                    "name": item.get("name"),
                    "biography": item.get("biography"),
                    "genres": item.get("genres", [])
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
