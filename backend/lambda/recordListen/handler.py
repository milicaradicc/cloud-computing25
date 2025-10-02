import os
import json
import boto3
import datetime

dynamodb = boto3.resource('dynamodb')
listening_history_table = dynamodb.Table(os.environ['LISTENING_HISTORY_TABLE'])
songs_table = dynamodb.Table(os.environ['SONGS_TABLE'])

def handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",   # ili precizan domen
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }

    try:
        # Ako nema Cognito authorizera (test invoke slučaj)
        try:
            user_id = event['requestContext']['authorizer']['claims']['sub']
        except Exception:
            print("Authorizer claims not found, fallback to test-user")
            user_id = "test-user"

        body = json.loads(event.get('body', '{}'))
        song_id = body.get('songId')
        album = body.get('album')

        if not song_id or not album:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'songId or album missing'})
            }

        # DynamoDB get_item sa oba ključa
        response = songs_table.get_item(
            Key={'Album': album, 'Id': song_id}
        )
        song_item = response.get('Item')

        if not song_item:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Song not found'})
            }

        # Zapis u istoriju slušanja
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        history_item = {
            'User': user_id,
            'TimeStamp': timestamp,
            'SongId': song_id,
            'Album': album,
            'Genre': song_item.get('Genre'),
            'Artist': song_item.get('Artist')
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
