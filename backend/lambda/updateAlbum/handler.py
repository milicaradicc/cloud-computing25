import json
import base64
import os
from datetime import datetime
import boto3

TABLE_NAME = os.environ["ALBUMS_TABLE"]
S3_BUCKET = os.environ.get("BUCKET_NAME")

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

album_table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "admin":
        return {
            "statusCode": 403,
            'headers': {'Access-Control-Allow-Origin': '*'},
            "body": json.dumps({"message": "Forbidden: Insufficient permissions"})
        }

    try:
        body = json.loads(event.get('body', '{}'))
        album_id = body.get('Id')
        album_title = body['title']
        genre = body['Genre']
        genres = body['genres']
        description = body.get('description', '')
        cover_image = body.get('coverImage', '')
        cover_base64 = body.get('coverBase64')  # Nova slika u base64

        if not album_id:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Album ID is required"})
            }

        if not genres or len(genres) == 0:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Album must have at least one genre"})
            }

        response = album_table.get_item(
            Key={
                'Genre': genre,
                'Id': album_id
            }
        )
        print(response)

        if 'Item' not in response:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Album not found"})
            }

        existing_album = response['Item']
        old_cover_image = existing_album.get('coverImage', '')

        # Ako postoji nova slika, uploaduj na S3
        if cover_base64:
            try:
                image_data = base64.b64decode(cover_base64)
                s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key=cover_image,
                    Body=image_data,
                    ContentType='image/jpeg'
                )
                print(f"Uploaded new cover image: {cover_image}")

                if old_cover_image and old_cover_image != cover_image:
                    try:
                        s3_client.delete_object(
                            Bucket=S3_BUCKET,
                            Key=old_cover_image
                        )
                        print(f"Deleted old cover image: {old_cover_image}")
                    except Exception as e:
                        print(f"Could not delete old image: {e}")

            except Exception as e:
                print(f"Error uploading to S3: {e}")
                return {
                    "statusCode": 500,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"message": f"Error uploading image: {str(e)}"})
                }

        final_cover_image = cover_image if cover_image else old_cover_image
        if genre not in genres:
            genre = genres[0]

        # Zadrži postojeće artiste, ne menja se ništa
        updated_item = {
            "Genre": genre,
            "Id": album_id,
            "title": album_title,
            "artists": existing_album.get('artists', []),
            "genres": genres,
            "releaseDate": existing_album.get('releaseDate', str(datetime.now())),
            "description": description,
            "coverImage": final_cover_image,
            "createdDate": existing_album.get('createdDate', str(datetime.now())),
            "modifiedDate": str(datetime.now()),
            "deleted": "false"
        }

        album_table.put_item(Item=updated_item)

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": f"Album '{album_title}' updated successfully.",
                "albumId": album_id,
                "item": updated_item
            }, default=str)
        }

    except Exception as e:
        import traceback
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
