import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("MusicStreamingApp")

def lambda_handler(event, context):
    artist_id = event.get('pathParameters', {}).get('artistId')
    if not artist_id:
        return {
            'statusCode': 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps({"error": "artistId is required"})
        }

    # Dohvati artist-a
    artist_response = table.query(
        IndexName="entityType-index",
        KeyConditionExpression=Key('entityType').eq('artist')
    )
    artist_items = [item for item in artist_response.get('Items', []) if item.get("artistId") == artist_id]

    if not artist_items:
        return {
            'statusCode': 404,
            "headers": {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps({"error": "Artist not found"})
        }

    artist_item = artist_items[0]
    artist = {
        "id": artist_item.get("artistId"),
        "name": artist_item.get("name"),
        "biography": artist_item.get("biography"),
        "imageUrl": artist_item.get("imageUrl", ""),
        "genres": artist_item.get("genres", [])
    }

    # Dohvati albume gde je artist u listi 'artists'
    albums = []
    last_evaluated_key = None
    while True:
        scan_kwargs = {
            "FilterExpression": Key('entityType').eq('album')
        }
        if last_evaluated_key:
            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

        response = table.scan(**scan_kwargs)
        for item in response.get('Items', []):
            if 'artists' in item and artist_id in item['artists']:
                albums.append({
                    "id": item.get("albumId") or item.get("Entity type identifier"),                    
                    "title": item.get("title"),
                    "year": item.get("year"),
                    "coverImage": item.get("coverImage", ""),
                    "description": item.get("description", ""),
                    "songs": item.get("songs", [])
                })

        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break

    return {
        'statusCode': 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        'body': json.dumps({
            "artist": artist,
            "albums": albums
        })
    }
