import json
import boto3
from boto3.dynamodb.conditions import Key

ses = boto3.client("ses", region_name="eu-north-1")
subs_table = boto3.resource("dynamodb").Table("Subscriptions")
SES_SOURCE_EMAIL = "milica.t.radic@gmail.com"

def lambda_handler(event, context):
    print("Event:", event)
    for record in event["Records"]:
        # 1. Extract SNS envelope
        sns_envelope = json.loads(record["body"])
        # 2. Parse album payload from Message field
        album = json.loads(sns_envelope["Message"])
        print("Parsed album:", album)

        genres = album.get("genres", [])
        print("Genres:", genres)
        artists = album.get("artists", [])
        print("Artists:", artists)

        # Query subscriptions by genre
        for genre in genres:
            resp = subs_table.query(
                KeyConditionExpression=Key("Target").eq("genre#" + genre)
            )
            subs = resp.get("Items", [])
            print(f"Subscriptions for genre {genre}:", subs)
            for sub in subs:
                # 👇 skipuj obrisane subscription-e
                if sub.get("deleted", "false") == "true":
                    continue
                email = sub.get("email")
                if email:
                    send_email(email, album)

        # Query subscriptions by artist
        for artist in artists:
            resp = subs_table.query(
                KeyConditionExpression=Key("Target").eq("artist#" + artist)
            )
            subs = resp.get("Items", [])
            print(f"Subscriptions for artist {artist}:", subs)
            for sub in subs:
                if sub.get("deleted", "false") == "true":
                    continue
                email = sub.get("email")
                if email:
                    send_email(email, album)


def send_email(user_email, album):
    print("Sending email to", user_email)
    """Send a well-formatted email notification about new album release"""

    title = album.get('title', 'Untitled Album')
    artists = album.get('artists', [])
    genres = album.get('genres', [])
    release_date = album.get('releaseDate', 'N/A')

    # Create an engaging email body
    subject = f"🎵 New Release: {title}"

    body = f"""Hello music lover!

Great news! A new album matching your interests is now available:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 Album: {title}

🎤 Artist(s): {', '.join(artists) if artists else 'Various Artists'}

🎸 Genre(s): {', '.join(genres) if genres else 'N/A'}

📅 Release Date: {release_date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Don't miss out on this new release! Start listening now and discover your next favorite track.

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
