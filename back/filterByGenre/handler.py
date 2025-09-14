import json
import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("MusicStreamingApp")

def decimal_default(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        # Uzmi query parametre
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

        albums = []
        artists = []
        last_evaluated_key = None

        # Paginate dok ne pokupimo sve rezultate
        while True:
            if last_evaluated_key:
                response = table.scan(
                    FilterExpression=Attr('genres').contains(genre),
                    ExclusiveStartKey=last_evaluated_key
                )
            else:
                response = table.scan(
                    FilterExpression=Attr('genres').contains(genre)
                )

            items = response.get('Items', [])

            for item in items:
                if 'entityType' not in item:
                    continue

                if item['entityType'] == 'album':
                    album = {
                        "id": item.get("albumId") or item.get("Entity type identifier"),
                        "title": item.get("title", ""),
                        "genres": item.get("genres", []),
                        "artists": item.get("artists", []),
                        "description": item.get("description", ""),
                        "coverImage": item.get("coverImage", None)
                    }
                    albums.append(album)

                elif item['entityType'] == 'artist':
                    artist = {
                        "id": item.get("artistId") or item.get("Entity type identifier"),
                        "name": item.get("name", ""),
                        "genres": item.get("genres", []),
                        "biography": item.get("biography", "")
                    }
                    artists.append(artist)

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

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
