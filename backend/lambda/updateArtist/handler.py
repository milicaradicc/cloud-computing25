import json
import boto3
import os
from boto3.dynamodb.conditions import Key

table_name = os.environ.get('ARTISTS_TABLE')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")
    if role != "admin":
        return {
            "statusCode": 403,
            'headers': {'Access-Control-Allow-Origin': '*'},
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }

    artist_id = event.get("pathParameters", {}).get("id")
    if not artist_id:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Missing artist id"})
        }

    try:
        body = json.loads(event.get("body", "{}"))
    except Exception:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Invalid JSON"})
        }

    name = body.get("name")
    biography = body.get("biography")
    genres = body.get("genres")

    if not name and not biography and not genres:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "No fields to update"})
        }

    try:
        response = table.query(
            IndexName="Id-index",
            KeyConditionExpression=Key("Id").eq(artist_id)
        )
        items = response.get("Items", [])
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Internal server error"})
        }

    if not items:
        return {
            "statusCode": 404,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Artist not found"})
        }

    artist = items[0]
    genre_pk = artist["Genre"]

    update_expr = []
    expr_attr_values = {}
    expr_attr_names = {}

    if name:
        update_expr.append("#N = :name")
        expr_attr_values[":name"] = name
        expr_attr_names["#N"] = "name"

    if biography:
        update_expr.append("biography = :bio")
        expr_attr_values[":bio"] = biography

    if genres and len(genres) > 0:
        update_expr.append("genres = :genres")
        expr_attr_values[":genres"] = genres

    update_expression = "SET " + ", ".join(update_expr)

    try:
        updated = table.update_item(
            Key={
                "Genre": genre_pk,
                "Id": artist_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_attr_values,
            ExpressionAttributeNames=expr_attr_names if expr_attr_names else None,
            ReturnValues="ALL_NEW"
        )
    except Exception:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Internal server error"})
        }

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({
            "message": "Artist updated",
            "artist": updated.get("Attributes")
        })
    }
