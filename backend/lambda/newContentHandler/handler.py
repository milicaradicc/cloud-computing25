import os
import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE'])
score_table = dynamodb.Table(os.environ['SCORE_TABLE'])

# Pretpostavka za težine, trebalo bi da budu iste kao u scoreUpdater
W_SUBSCRIPTION = 0.4 

def handler(event, context):
    # 1. Parsiraj poruku sa SNS-a
    message = json.loads(event['Records'][0]['Sns']['Message'])
    genre = message.get('genre')
    artist = message.get('artistId')
    content_id = message.get('contentId') # Npr. ID novog albuma/pesme

    if not content_id or (not genre and not artist):
        print("Missing data in SNS message")
        return

    # 2. Pronađi sve korisnike koji su pretplaćeni na žanr ili izvođača
    users_to_notify = set()
    
    # Koristimo PK Subscriptions tabele (Target)
    if genre:
        response_genre = subscriptions_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('Target').eq(f"genre#{genre}")
        )
        for item in response_genre.get('Items', []):
            users_to_notify.add(item['User'])

    if artist:
        response_artist = subscriptions_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('Target').eq(f"artist#{artist}")
        )
        for item in response_artist.get('Items', []):
            users_to_notify.add(item['User'])

    # 3. Za svakog korisnika, upiši visok početni skor za novi sadržaj
    for user_id in users_to_notify:
        try:
            # Dajemo visok početni skor da bi se pojavilo na vrhu feed-a
            initial_sub_score = 1
            initial_recency_score = 1 # Smatramo ga "najsvežijim"
            total_score = (Decimal(initial_sub_score) * Decimal(W_SUBSCRIPTION)) # + ... ostali skorovi

            score_table.put_item(
                Item={
                    'User': user_id,
                    'Content': content_id,
                    'sub_score': initial_sub_score,
                    'recency_score': initial_recency_score,
                    'total_score': total_score
                }
            )
            print(f"Pushed new content {content_id} to user {user_id}")
        except Exception as e:
            print(f"Error pushing content to user {user_id}: {e}")

    return {'statusCode': 200, 'body': 'OK'}