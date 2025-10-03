import os
import json
import boto3
import datetime

dynamodb = boto3.resource('dynamodb')
listening_history_table = dynamodb.Table(os.environ['LISTENING_HISTORY_TABLE'])
songs_table = dynamodb.Table(os.environ['SONGS_TABLE'])

def handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }

    try:
        try:
            user_id = event['requestContext']['authorizer']['claims']['sub']
        except Exception:
            print("Authorizer claims not found, fallback to test-user")
            user_id = "test-user"

        body = json.loads(event.get('body', '{}'))
        song_id = body.get('songId')
        album = body.get('album')
        album_id = album['Id']

        if not song_id or not album:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'songId or album missing'})
            }

        response = songs_table.get_item(
            Key={'Album': album_id, 'Id': song_id}
        )
        song_item = response.get('Item')
        print("Song item:", song_item)
        if not song_item:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Song not found'})
            }

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Uzima prvi genre i prvi artist iz liste (ako postoji)
        first_genre = song_item.get('genres', [None])[0]
        first_artist = song_item.get('artists', [None])[0]

        history_item = {
            'User': user_id,
            'TimeStamp': timestamp,
            'SongId': song_id,
            'Album': album,
            'Genre': first_genre,
            'Artist': first_artist
        }

        listening_history_table.put_item(Item=history_item)

        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({'message': 'Listen event recorded'})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
