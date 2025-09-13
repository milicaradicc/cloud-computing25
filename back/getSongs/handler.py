import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
client = boto3.client('dynamodb')
table = dynamodb.Table("MusicStreamingApp")

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
                                "Entity type identifier": {"S": aid},
                                "Entity-specific identifier": {"S": "PROFILE"}
                            }
                            for aid in batch_ids
                        ]
                        batch_response = client.batch_get_item(
                            RequestItems={
                                table.name: {
                                    "Keys": keys
                                }
                            }
                        )
                        artists_details.extend(
                            [{k: v['S'] for k, v in artist.items()} for artist in batch_response['Responses'].get(table.name, [])]
                        )

                song = {
                    "title": item['title'],
                    "artists": artists_details,  # full artist objects
                    "genres": item.get('genres', []),
                    "description": item.get('description', ''),
                    "coverImage": item.get('coverImage'),
                    "album": item.get('album'),
                }
                songs.append(song)

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        return {
            'statusCode': 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps(songs)
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            'body': json.dumps({"error": str(e)})
        }
