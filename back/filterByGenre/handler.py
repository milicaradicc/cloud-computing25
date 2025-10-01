import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
artists_table = dynamodb.Table("Artists")
albums_table = dynamodb.Table("Album")

def decimal_default(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters') or {}
        genre = query_params.get('genre')

        if not genre:
            return {
                'statusCode': 400,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                'body': json.dumps({"message": "Missing 'genre' query parameter"})
            }

        artists_response = artists_table.query(
            KeyConditionExpression=Key('Genre').eq(genre)
        )
        artists = []
        for item in artists_response.get('Items', []):
            artist = {
                "id": item.get("Id"),
                "name": item.get("name", ""),
                "genres": item.get("genres", []),
                "biography": item.get("biography", "")
            }
            artists.append(artist)

        albums_response = albums_table.query(
            KeyConditionExpression=Key('Genre').eq(genre)
        )
        albums = []
        for item in albums_response.get('Items', []):
            album = {
                "id": item.get("Id"),
                "title": item.get("title", ""),
                "genres": item.get("genres", []),
                "artists": item.get("artists", []),
                "description": item.get("description", ""),
                "coverImage": item.get("coverImage", None)
            }
            albums.append(album)

        result = {
            "albums": albums,
            "artists": artists
        }

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps(result, default=decimal_default)
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error: {error_trace}")
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"error": str(e), "trace": error_trace})
        }
