import os
import boto3
from boto3.dynamodb.conditions import Key
from collections import defaultdict
import json
import traceback

dynamodb = boto3.resource('dynamodb')

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}

def handler(event, context):
    print("=== Lambda invoked ===")
    print("Event:", json.dumps(event))  # Loguj ceo event

    try:
        score_table = dynamodb.Table(os.environ['SCORE_TABLE'])
        songs_table = dynamodb.Table(os.environ['SONGS_TABLE'])
        albums_table = dynamodb.Table(os.environ['ALBUMS_TABLE'])
        print("Tables loaded:", os.environ['SCORE_TABLE'], os.environ['SONGS_TABLE'], os.environ['ALBUMS_TABLE'])

        try:
            user_id = event['requestContext']['authorizer']['claims']['sub']
            print("User ID from Cognito:", user_id)
        except (KeyError, TypeError):
            query_params = event.get('queryStringParameters') or {}
            user_id = query_params.get('userId', 'test-user')
            print("Using fallback user_id:", user_id)

        # 1️⃣ Dobavi top artist i top genre
        print("Querying Score table for user...")
        response = score_table.query(
            IndexName='User-index',
            KeyConditionExpression=Key('User').eq(user_id)
        )
        items = response.get('Items', [])
        print(f"Found {len(items)} score records")

        if not items:
            print("No score records found")
            return {
                'statusCode': 200,
                'headers': HEADERS,
                'body': json.dumps({
                    'topArtist': None,
                    'topGenre': None,
                    'songs': [],
                    'albums': [],
                    'message': 'No listening history yet'
                })
            }

        aggregated = defaultdict(lambda: {"total_sum": 0, "total_number": 0})
        for r in items:
            content = r.get("Content")
            print(content)
            if not content:
                continue
            aggregated[content]["total_sum"] += float(r.get("sum", 0))
            aggregated[content]["total_number"] += int(r.get("number", 0))
        print("Aggregated scores:", aggregated)
        print("Aggregated items: ", aggregated.items())
        results = []

        for content, data in aggregated.items():
            if data["total_number"] > 0:
                avg = data["total_sum"] / data["total_number"]
            else:
                avg = 0
            results.append({"Content": content, "Average": round(avg, 2)})

        print("Calculated averages:", results)

        artists = [r for r in results if r["Content"][:7] == "ARTIST#"]
        genres = [r for r in results if r["Content"][:6] == "GENRE#"]

        print(f"Artists found: {artists}")
        print(f"Genres found: {genres}")

        top_artist = max(artists, key=lambda x: x["Average"], default=None)
        top_genre = max(genres, key=lambda x: x["Average"], default=None)
        print("Top artist:", top_artist)
        print("Top genre:", top_genre)

        top_artist_id = top_artist["Content"].replace("ARTIST#", "") if top_artist else None
        top_genre_name = top_genre["Content"].replace("GENRE#", "") if top_genre else None

        # 2️⃣ Prikupljanje pesama i albuma preko GSI
        songs_set = set()
        albums_set = set()
        songs = []
        albums = []

        # Pesme i albumi po artistu
        if top_artist_id:
            print(f"Querying Songs and Albums by ArtistId={top_artist_id}")
            resp_songs = songs_table.query(
                IndexName='artist-index',
                KeyConditionExpression=Key('artist').eq(top_artist_id)
            )
            for s in resp_songs.get('Items', []):
                songs_set.add(s['Id'])
                songs.append(s)
            print(f"Songs by artist: {len(resp_songs.get('Items', []))}")

            resp_albums = albums_table.query(
                IndexName='artist-index',
                KeyConditionExpression=Key('artist').eq(top_artist_id)
            )
            for a in resp_albums.get('Items', []):
                albums_set.add(a['Id'])
                albums.append(a)
            print(f"Albums by artist: {len(resp_albums.get('Items', []))}")

        # Pesme i albumi po žanru
        if top_genre_name:
            print(f"Querying Songs and Albums by Genre={top_genre_name}")
            resp_songs = songs_table.query(
                IndexName='genre-index',
                KeyConditionExpression=Key('genre').eq(top_genre_name)
            )
            for s in resp_songs.get('Items', []):
                if s['Id'] not in songs_set:
                    songs_set.add(s['Id'])
                    songs.append(s)
            print(f"Songs by genre: {len(resp_songs.get('Items', []))}")

            resp_albums = albums_table.query(
                IndexName='Genre-index',
                KeyConditionExpression=Key('Genre').eq(top_genre_name)
            )
            for a in resp_albums.get('Items', []):
                if a['Id'] not in albums_set:
                    albums_set.add(a['Id'])
                    albums.append(a)
            print(f"Albums by genre: {len(resp_albums.get('Items', []))}")

        print(f"Total songs: {len(songs)}, Total albums: {len(albums)}")

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps({
                'topArtist': top_artist,
                'topGenre': top_genre,
                'songs': songs,
                'albums': albums
            })
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps({'error': str(e), 'type': type(e).__name__})
        }
