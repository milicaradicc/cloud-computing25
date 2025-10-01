import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import os

ARTISTS_TABLE_NAME = os.environ["ARTISTS_TABLE_NAME"]
ARTIST_ALBUM_TABLE_NAME = os.environ["ARTIST_ALBUM_TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")

artists_table = dynamodb.Table(ARTISTS_TABLE_NAME)
artist_album_table = dynamodb.Table(ARTIST_ALBUM_TABLE_NAME)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        path_params = event.get('pathParameters', {})
        artist_id = path_params.get('id')

        query_params = event.get('queryStringParameters')
        if query_params is None:
            query_params = {}
        genre = query_params.get('genre')

        if not artist_id or not genre:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Both 'id' path parameter and 'genre' query parameter are required"})
            }

        artist_response = artists_table.get_item(
            Key={
                "Genre": genre,
                "Id": artist_id
            }
        )
        
        artist_details = artist_response.get("Item")
        if not artist_details:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Artist not found with the specified ID and Genre"})
            }
        
        albums_response = artist_album_table.query(
            KeyConditionExpression=Key("ArtistId").eq(artist_id)
        )
        
        albums = albums_response.get("Items", [])

        artist_details["albums"] = albums
        
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps(artist_details, cls=DecimalEncoder)
        }

    except Exception as e:
        print(f"Error: {str(e)}") 
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)})
        }

