import os
import json
import boto3
import datetime

dynamodb = boto3.resource('dynamodb')
listening_history_table = dynamodb.Table(os.environ['LISTENING_HISTORY_TABLE'])
# Potrebna nam je i Songs tabela da bismo znali žanr/izvođača pesme
songs_table = dynamodb.Table(os.environ['SONGS_TABLE']) 

def handler(event, context):
    """
    Beleži da je korisnik odslušao pesmu.
    """
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        body = json.loads(event['body'])
        song_id = body['songId']

        # 1. Dobavi info o pesmi da scoreUpdater zna o kom žanru/izvođaču se radi
        # NAPOMENA: Proveri da li je 'Id' ispravan Partition Key za tvoju Songs tabelu
        response = songs_table.get_item(Key={'Id': song_id})
        song_item = response.get('Item')
        
        if not song_item:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Song not found'})}

        # 2. Kreiraj novi zapis za istoriju slušanja
        # Timestamp je naš Sort Key, mora biti jedinstven za svaki događaj
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        history_item = {
            'User': user_id,
            'Timestamp': timestamp,
            'SongId': song_id,
            'Genre': song_item.get('Genre'),
            'Artist': song_item.get('Artist') 
            # Dodajemo Genre i Artist da bi scoreUpdater imao sve potrebne podatke
        }

        listening_history_table.put_item(Item=history_item)

        return {
            'statusCode': 201, # 201 Created
            'body': json.dumps({'message': 'Listen event recorded'})
        }
    except Exception as e:
        print(e)
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}