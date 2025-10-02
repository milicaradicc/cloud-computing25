import json
import os
import boto3
import uuid
import os

songs_table_name = os.environ["SONGS_TABLE"]
songs_table_partition_key = os.environ["SONGS_TABLE_PK"]
songs_table_sort_key = os.environ["SONGS_TABLE_SK"]

dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(songs_table_name)

def lambda_handler(event, context):
    song_id=event['songId']
    transcript_filename=event['jobName']+'.json'

    response = songs_table.query(
            IndexName="Id-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("Id").eq(song_id)
        )
    items = response.get("Items", [])
    item = items[0]

    songs_table.update_item(
        Key={
            songs_table_partition_key: item[songs_table_partition_key],
            songs_table_sort_key: item[songs_table_sort_key]
        },
        UpdateExpression="SET transcriptPath = :tp",
        ExpressionAttributeValues={
            ":tp": transcript_filename
        }
    )
