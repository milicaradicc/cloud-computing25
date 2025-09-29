import json
import boto3
from boto3.dynamodb.conditions import Key

ses = boto3.client("ses", region_name="eu-north-1")
subs_table = boto3.resource("dynamodb").Table("Subscriptions")
SES_SOURCE_EMAIL = "milica.t.radic@gmail.com"

def lambda_handler(event, context):
    print("Event:", event)
    for record in event["Records"]:
        sns_envelope = json.loads(record["body"])
        song = json.loads(sns_envelope["Message"])
        print("Parsed song:", song)

        genres = song.get("genres", [])
        artists = song.get("artists", [])

        # Query subscriptions by genre
        for genre in genres:
            resp = subs_table.query(KeyConditionExpression=Key("Target").eq("genre#" + genre))
            for sub in resp.get("Items", []):
                # 👇 preskoči obrisane subscription-e
                if sub.get("deleted", "false") == "true":
                    continue
                email = sub.get("email")
                if email:
                    send_email(email, song)

        # Query subscriptions by artist
        for artist in artists:
            resp = subs_table.query(KeyConditionExpression=Key("Target").eq("artist#" + artist))
            for sub in resp.get("Items", []):
                if sub.get("deleted", "false") == "true":
                    continue
                email = sub.get("email")
                if email:
                    send_email(email, song)

def send_email(user_email, song):
    print("Sending email to", user_email)
    title = song.get('title', 'Untitled Song')
    artists = song.get('artists', [])
    genres = song.get('genres', [])
    release_date = song.get('releaseDate', 'N/A')

    subject = f"🎵 New Single: {title}"
    body = f"""Hello music lover!

A new single matching your interests is now available:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 Song: {title}

🎤 Artist(s): {', '.join(artists) if artists else 'Various Artists'}

🎸 Genre(s): {', '.join(genres) if genres else 'N/A'}

📅 Release Date: {release_date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Don't miss out on this new single! Listen now and discover your next favorite track.

Happy listening!

---
You're receiving this because you subscribed to notifications for {', '.join(genres[:2]) if genres else ', '.join(artists[:2])}.
To manage your subscriptions, please contact support.
"""

    ses.send_email(
        Source=SES_SOURCE_EMAIL,
        Destination={"ToAddresses": [user_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        }
    )
