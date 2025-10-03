import datetime
import os
import boto3
import logging
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
score_table_name = os.environ['SCORE_TABLE']
rating_table_name = os.environ['RATING_TABLE']
subscription_table_name = os.environ['SUBSCRIPTION_TABLE']

score_table = dynamodb.Table(score_table_name)
rating_table = dynamodb.Table(rating_table_name)
subscription_table = dynamodb.Table(subscription_table_name)

W_RATING = 0.5
W_SUBSCRIPTION = 0.4
W_RECENCY = 0.2

def handler(event, context):
    logger.info(f"Received {len(event['Records'])} records to process.")

    for record in event['Records']:
        try:
            event_name = record['eventName']
            
            if event_name in ['INSERT', 'MODIFY']:
                source_arn = record['eventSourceARN']
                image = record['dynamodb']['NewImage']
                user_id = image.get('User', {}).get('S')
                
                if not user_id: continue
                
                if 'Ratings' in source_arn:
                    handle_rating_update(user_id, image)
                elif 'Subscriptions' in source_arn:
                    handle_subscription_update(user_id, image, is_subscribed=True)
                elif 'ListeningHistory' in source_arn:
                    handle_listening_history_update(user_id, image)
            
            # NOVO: Blok za obradu REMOVE događaja
            elif event_name == 'REMOVE':
                source_arn = record['eventSourceARN']
                image = record['dynamodb']['OldImage']
                user_id = image.get('User', {}).get('S')

                if not user_id: continue
                
                if 'Subscriptions' in source_arn:
                    handle_subscription_update(user_id, image, is_subscribed=False)

        except Exception as e:
            logger.error(f"Error processing record: {record}")
            logger.error(f"Exception: {e}")
            continue

    return {
        'statusCode': 200,
        'body': 'Successfully processed records.'
    }

def handle_rating_update(user_id, new_image):
    # --- AVG GENRE ---
    genre = new_image.get('Genre', {}).get('S')
    if genre:
        content_id_genre = f"genre#{genre}"
        user_genre_key = f"{user_id}_genre#{genre}"
        
        response_genre = rating_table.query(
            IndexName="UserGenreIndex",
            # ISPRAVKA: Koristimo ispravnu 'Key' klasu
            KeyConditionExpression=Key('UserGenre').eq(user_genre_key)
        )
        
        items_genre = response_genre.get('Items', [])
        if items_genre:
            avg_rating_genre = sum(item['Rating'] for item in items_genre) / len(items_genre)
            update_score(user_id, content_id_genre, {'avg_rating': avg_rating_genre})

    # --- AVG ARTIST ---
    artist = new_image.get('Artist', {}).get('S') 
    if artist:
        content_id_artist = f"artist#{artist}"
        user_artist_key = f"{user_id}_artist#{artist}"

        response_artist = rating_table.query(
            IndexName="UserArtistIndex",
            # ISPRAVKA: Koristimo ispravnu 'Key' klasu
            KeyConditionExpression=Key('UserArtist').eq(user_artist_key)
        )
        
        items_artist = response_artist.get('Items', [])
        if items_artist:
            avg_rating_artist = sum(item['Rating'] for item in items_artist) / len(items_artist)
            update_score(user_id, content_id_artist, {'avg_rating': avg_rating_artist})

def handle_subscription_update(user_id, image, is_subscribed):
    """
    Obrađuje događaje upisa (subscribe) i brisanja (unsubscribe).
    
    Args:
        user_id (str): ID korisnika.
        image (dict): DynamoDB slika reda ('NewImage' ili 'OldImage').
        is_subscribed (bool): True ako je INSERT/MODIFY, False ako je REMOVE.
    """
    # 'Target' je PK u Subscriptions tabeli (npr. 'genre#Pop' ili 'artist#xyz')
    content_id = image['Target']['S']
    
    # NOVO: Vrednost sub_score zavisi od toga da li je korisnik
    # upisan (True -> 1) ili se odjavio (False -> 0).
    new_sub_score = 1 if is_subscribed else 0
    
    action_text = "Subscribed" if is_subscribed else "Unsubscribed"
    logger.info(f"Processing '{action_text}' for {user_id} on {content_id}. Setting sub_score to {new_sub_score}")
    
    # Pozivamo update_score sa dinamički određenom vrednošću
    update_score(user_id, content_id, {'sub_score': new_sub_score})

def handle_listening_history_update(user_id, new_image):
    content_id = f"genre#{new_image['Genre']['S']}"
    timestamp_str = new_image['Timestamp']['S']
    
    # 1. Izračunaj koliko je dana prošlo
    listen_time = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    now = datetime.datetime.now(datetime.timezone.utc)
    days_passed = (now - listen_time).days
    
    # 2. Primeni formulu za opadanje skora (decay function)
    # Skor će biti 1.0 ako je slušano danas, 0.5 ako je juče, 0.33 pre dva dana, itd.
    recency_score = Decimal(1 / (days_passed + 1))
    
    logger.info(f"Calculated recency score for {user_id} on {content_id}: {recency_score:.2f}")
    
    update_score(user_id, content_id, {
        'recency_score': recency_score,
        'last_played': timestamp_str,
        'increment_listen_count': True # Specijalni signal za update_score funkciju
    })

def update_score(user_id, content_id, new_values):
    """
    Centralna funkcija za ažuriranje Score tabele sa podrškom za atomički inkrement.
    """
    try:
        # 1. Prvo, pročitaj postojeće vrednosti da bismo izračunali TotalScore
        response = score_table.get_item(
            Key={'User': user_id, 'Content': content_id}
        )
        item = response.get('Item', {})

        # 4. Kreiraj UpdateExpression i pripremi vrednosti
        update_expression = "SET "
        # NOVO: Inicijalizujemo expression_values sa placeholder-ima za brojač
        expression_values = {':one': Decimal(1), ':zero': Decimal(0)}
        
        # NOVO: Specijalna logika za atomično povećavanje brojača
        if new_values.get('increment_listen_count'):
            # if_not_exists osigurava da brojač krene od 0 ako ne postoji
            update_expression += "listen_count = if_not_exists(listen_count, :zero) + :one, "
            # Uklanjamo signal da se ne bi upisao kao običan atribut
            del new_values['increment_listen_count']

        # 2. Spoji stare i nove vrednosti (nakon obrade signala)
        item.update(new_values)

        # 3. Izračunaj novi TotalScore
        avg_rating = item.get('avg_rating', 0)
        sub_score = item.get('sub_score', 0)
        recency_score = item.get('recency_score', 0)
        # listen_count takođe možeš uključiti u formulu ako želiš, npr. sa malim težinskim faktorom
        
        total_score = (Decimal(avg_rating) * Decimal(W_RATING)) + \
                      (Decimal(sub_score) * Decimal(W_SUBSCRIPTION)) + \
                      (Decimal(recency_score) * Decimal(W_RECENCY))
        
        item['total_score'] = total_score
        
        # Nastavljamo sa izgradnjom UpdateExpression-a za ostale atribute
        for key, value in item.items():
            # NOVO: Preskačemo ključeve i listen_count koji je već obrađen na poseban način
            if key not in ['User', 'Content', 'listen_count']:
                expression_key = f":{key}"
                update_expression += f"{key} = {expression_key}, "
                expression_values[expression_key] = value

        # Ukloni poslednji zarez i razmak
        update_expression = update_expression[:-2]

        # 5. Izvrši ažuriranje
        score_table.update_item(
            Key={'User': user_id, 'Content': content_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        logger.info(f"Successfully updated score for {user_id} on {content_id}. New TotalScore: {total_score}")

    except Exception as e:
        logger.error(f"Failed to update score for {user_id} on {content_id}. Error: {e}")