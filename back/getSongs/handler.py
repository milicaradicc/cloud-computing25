import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
client = boto3.client('dynamodb')
table = dynamodb.Table("MusicStreamingApp")

def decimal_default(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        songs = []
        last_evaluated_key = None

        while True:
            if last_evaluated_key:
                response = table.query(
                    IndexName="entityType-index",
                    KeyConditionExpression=Key('entityType').eq('song'),
                    ExclusiveStartKey=last_evaluated_key
                )
            else:
                response = table.query(
                    IndexName="entityType-index",
                    KeyConditionExpression=Key('entityType').eq('song')
                )

            items = response.get('Items', [])
            for item in items:
                artist_ids = item.get('artists', [])
                artists_details = []

                if artist_ids:
                    for i in range(0, len(artist_ids), 100):
                        batch_ids = artist_ids[i:i+100]
                        keys = [
                            {
                                "Entity type identifier": {"S": f"ARTIST#{aid}"},
                                "Entity-specific identifier": {"S": "PROFILE"}
                            }
                            for aid in batch_ids
                        ]
                        batch_response = client.batch_get_item(
                            RequestItems={table.name: {"Keys": keys}}
                        )
                        for artist in batch_response['Responses'].get(table.name, []):
                            artist_detail = {}
                            for key, value in artist.items():
                                if 'S' in value:
                                    artist_detail[key] = value['S']
                                elif 'SS' in value:
                                    artist_detail[key] = value['SS']
                                elif 'L' in value:
                                    artist_detail[key] = [i.get('S', '') for i in value['L']]
                            artists_details.append(artist_detail)

                song = {
                    "id": item.get('Entity type identifier', '').replace('SONG#', ''),
                    "title": item['title'],
                    "artists": artists_details,
                    "genres": item.get('genres', []),
                    "description": item.get('description', ''),
                    "coverImage": item.get('coverImage'),
                    "album": item.get('album'),
                    "duration": item.get('duration'),
                    "releaseDate": item.get('releaseDate'),
                    "type": item.get('type', 'single')
                }
                songs.append(song)

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        print(f"Found {len(songs)} songs")

        return {
            'statusCode': 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps(songs, default=decimal_default)  # ⇐ OVDE DODATO
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error occurred: {error_trace}")

        return {
            'statusCode': 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"error": str(e), "trace": error_trace})
        }
