import json
import os
import boto3
from boto3.dynamodb.conditions import Key

# SES setup iz env
region = os.environ.get("SES_REGION", os.environ["AWS_REGION"])
SES_SOURCE_EMAIL = os.environ["SES_SOURCE_EMAIL"]

ses = boto3.client("ses", region_name=region)
subs_table = boto3.resource("dynamodb").Table(os.environ["SUBSCRIPTIONS_TABLE"])


def lambda_handler(event, context):
    print("Event:", event)
    for record in event["Records"]:
        sns_envelope = json.loads(record["body"])
        message = json.loads(sns_envelope["Message"])
        attributes = sns_envelope.get("MessageAttributes", {})

        content_type = attributes.get("contentType", {}).get("Value", "song")
        print("Content type:", content_type)
        print("Parsed message:", message)

        # izvuci interese za korisnike
        genres = message.get("genres", [])
        artists = message.get("artists", [])

        # Query subscriptions by genre
        for genre in genres:
            resp = subs_table.query(
                KeyConditionExpression=Key("Target").eq("genre#" + genre)
            )
            for sub in resp.get("Items", []):
                if sub.get("deleted", "false") == "true":
                    continue
                email = sub.get("email")
                if email:
                    send_email(email, message, content_type)

        # Query subscriptions by artist
        for artist in artists:
            resp = subs_table.query(
                KeyConditionExpression=Key("Target").eq("artist#" + artist)
            )
            for sub in resp.get("Items", []):
                if sub.get("deleted", "false") == "true":
                    continue
                email = sub.get("email")
                if email:
                    send_email(email, message, content_type)


def send_email(user_email, message, content_type):
    print(f"Sending {content_type} email to {user_email}")

    if content_type == "album":
        subject = f"📀 New Album: {message.get('title', 'Untitled Album')}"
        body = f"""Hello music lover!

A new album has just been released:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📀 Album: {message.get('title', 'Untitled Album')}
🎤 Artist(s): {', '.join(message.get('artists', [])) or 'Various Artists'}
🎸 Genre(s): {', '.join(message.get('genres', [])) or 'N/A'}
📅 Release Date: {message.get('releaseDate', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dive into the full album and enjoy all the new tracks!

---
You're receiving this because you subscribed to notifications for your favorite artists/genres.
"""
    else:  # default song
        subject = f"🎵 New Single: {message.get('title', 'Untitled Song')}"
        body = f"""Hello music lover!

A new single matching your interests is now available:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 Song: {message.get('title', 'Untitled Song')}
🎤 Artist(s): {', '.join(message.get('artists', [])) or 'Various Artists'}
🎸 Genre(s): {', '.join(message.get('genres', [])) or 'N/A'}
📅 Release Date: {message.get('releaseDate', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Don't miss out on this new single! Listen now and discover your next favorite track.

---
You're receiving this because you subscribed to notifications for your favorite artists/genres.
"""

    ses.send_email(
        Source=SES_SOURCE_EMAIL,
        Destination={"ToAddresses": [user_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    )
