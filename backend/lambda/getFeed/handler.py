import os
import json
import boto3
from boto3.dynamodb.conditions import Key

# Inicijalizacija svih potrebnih tabela
dynamodb = boto3.resource('dynamodb')

# Imena tabela iz environment varijabli (prosledi ih u CDK-u)
score_table = dynamodb.Table(os.environ['SCORE_TABLE'])
songs_table = dynamodb.Table(os.environ['SONGS_TABLE'])
albums_table = dynamodb.Table(os.environ['ALBUMS_TABLE'])
artist_song_table = dynamodb.Table(os.environ['ARTIST_SONG_TABLE'])
artist_album_table = dynamodb.Table(os.environ['ARTIST_ALBUM_TABLE'])


def handler(event, context):
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']

        # === KORAK 1: Pronađi korisnikove omiljene žanrove i izvođače ===
        response = score_table.query(
            IndexName="UserTotalScoreIndex",
            KeyConditionExpression=Key('User').eq(user_id),
            ScanIndexForward=False, # Sortiraj opadajuće
            Limit=5 # Uzimamo top 5 interesovanja kao osnovu za preporuke
        )
        
        top_interests = response.get('Items', [])
        
        top_genres = [item['Content'].split('#')[1] for item in top_interests if item['Content'].startswith('genre#')]
        top_artists = [item['Content'].split('#')[1] for item in top_interests if item['Content'].startswith('artist#')]

        # === KORAK 2: Prikupi pesme i albume na osnovu interesovanja ===
        recommended_songs = {} # Koristimo dictionary da izbegnemo duplikate
        recommended_albums = {}

        # Preporuke po žanru
        for genre in top_genres:
            # Pesme
            songs_response = songs_table.query(
                IndexName="GenreRatingIndex",
                KeyConditionExpression=Key('Genre').eq(genre),
                ScanIndexForward=False,
                Limit=10
            )
            for song in songs_response.get('Items', []):
                recommended_songs[song['Id']] = song

            # Albumi
            albums_response = albums_table.query(
                IndexName="GenreRatingIndex",
                KeyConditionExpression=Key('Genre').eq(genre),
                ScanIndexForward=False,
                Limit=10
            )
            for album in albums_response.get('Items', []):
                recommended_albums[album['Id']] = album

        # Preporuke po izvođaču
        for artist_id in top_artists:
            # Pesme (preko mapping tabele)
            song_ids_response = artist_song_table.query(
                KeyConditionExpression=Key('ArtistId').eq(artist_id),
                Limit=10
            )
            # Ovde bi bio potreban BatchGetItem da se dobiju detalji za svaku pesmu
            # Zbog jednostavnosti, preskačemo taj deo za sada

            # Albumi (preko mapping tabele)
            album_ids_response = artist_album_table.query(
                KeyConditionExpression=Key('ArtistId').eq(artist_id),
                Limit=10
            )
            # Slično, BatchGetItem za detalje o albumima

        # === KORAK 3: Sastavi finalni feed ===
        final_songs = list(recommended_songs.values())[:10]
        final_albums = list(recommended_albums.values())[:10]

        feed = {
            'recommendedSongs': final_songs,
            'recommendedAlbums': final_albums
        }

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',  
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body': json.dumps(feed, default=str)
        }
    except Exception as e:
        print(e)
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}