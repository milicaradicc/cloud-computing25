import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("Song")

def decimal_default(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        path_params = event.get("pathParameters", {})
        song_id = path_params.get("songId")

        # Scan po celoj tabeli da nadjemo pesmu sa datim Id-em
        # (alternativa je imati GSI po Id-u za efikasnije query)
        last_evaluated_key = None
        item = None
        while True:
            if last_evaluated_key:
                response = table.scan(ExclusiveStartKey=last_evaluated_key)
            else:
                response = table.scan()

            for i in response.get("Items", []):
                if i.get("Id") == song_id:
                    item = i
                    break
            if item:
                break
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

        if not item:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Song not found"})
            }

        # Ovde možeš dodati logiku da fetch-uješ ARTIST detalje ako želiš
        artists_details = item.get("artists", [])

        # Ako song ima album, možeš pokušati fetch albuma
        album_id = item.get("album")
        album_title = None
        if album_id:
            album_response = table.scan()  # po potrebi možeš optimizovati query
            for alb in album_response.get("Items", []):
                if alb.get("Id") == album_id:
                    album_title = alb.get("title")
                    break

        song = {
            "id": item.get("Id"),
            "title": item.get("title"),
            "artists": artists_details,
            "genres": item.get("genres", []),
            "description": item.get("description", ""),
            "coverImage": item.get("coverImage"),
            "album": album_title,
            "duration": item.get("duration"),
            "releaseDate": item.get("releaseDate"),
            "type": item.get("type", "single"),
            "fileName": item.get("fileName", "")
        }

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps(song, default=decimal_default)
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error occurred: {error_trace}")

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": str(e), "trace": error_trace})
        }
