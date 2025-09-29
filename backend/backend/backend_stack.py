from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
)

from backend.cognito_setup import setup_cognito


class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "BackendQueue",
            visibility_timeout=Duration.seconds(300),
        )

        topic = sns.Topic(
            self, "BackendTopic"
        )

        topic.add_subscription(subs.SqsSubscription(queue))

        # API Gateway
        # api = apigw.RestApi(self, "MusicAppApi", rest_api_name="Songs Service")

        # S3 bucket
        music_bucket = s3.Bucket(
            self, "my-music-app-files",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # dynamo tables
        songs_table = dynamodb.Table(
            self, "Songs",
            partition_key=dynamodb.Attribute(
                name="Album",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="Id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        albums_table = dynamodb.Table(
            self, "Albums",
            partition_key=dynamodb.Attribute(
                name="Genre",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="Id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        artists_table = dynamodb.Table(
            self, "Artists",
            partition_key=dynamodb.Attribute(
                name="Genre",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="Id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        user_pool, user_pool_client = setup_cognito(self)

        # # lambde
        # # 1. create artist
        # create_artist_lambda = _lambda.Function(
        #     self, "CreateArtistLambda",
        #     runtime=_lambda.Runtime.PYTHON_3_13,
        #     handler="handler.lambda_handler",
        #     code=_lambda.Code.from_asset("createArtist")
        # )

        # upload_file_lambda = _lambda.Function(
        #     self, "UploadFileLambda",
        #     runtime=_lambda.Runtime.PYTHON_3_13,
        #     handler="create_song.handler",
        #     code=_lambda.Code.from_asset("lambda")
        # )



        # # nista ovo nije odradjeno jos ⬇️ samo su primeri komandi

        # # Root resource: /songs
        # songs_resource = api.root.add_resource("songs")

        # # Dodaj GET metodu -> get_songs_lambda
        # songs_resource.add_method("GET", apigw.LambdaIntegration(get_songs_lambda))

        # # Dodaj POST metodu -> create_song_lambda
        # songs_resource.add_method("POST", apigw.LambdaIntegration(create_song_lambda))


        # # Primer: dodela permisija Lambda funkciji da piše u bucket
        # music_bucket.grant_read_write(create_song_lambda)