from constructs import Construct
from aws_cdk import aws_apigateway as apigateway,aws_iam as iam, aws_lambda as _lambda, aws_dynamodb as dynamodb
from backend.utils.create_lambda import create_lambda_function

class SubscriptionsConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        api: apigateway.RestApi,
        table: dynamodb.Table,
        authorizer
    ):
        super().__init__(scope, id)

        subscriptions_api_resource = api.root.add_resource("subscriptions")

        # Create Subscription
        create_subscription_lambda = create_lambda_function(
            self,
            "CreateSubscriptionLambda",
            "handler.lambda_handler",
            "lambda/createSubscription",
            [],
            {"SUBSCRIPTIONS_TABLE": table.table_name}
        )
        table.grant_read_write_data(create_subscription_lambda)

        subscriptions_api_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(create_subscription_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Get Subscriptions
        get_subscriptions_lambda = create_lambda_function(
            self,
            "GetSubscriptionsLambda",
            "handler.lambda_handler",
            "lambda/getSubscriptionsByUser",
            [],
            {"SUBSCRIPTIONS_TABLE": table.table_name}
        )
        table.grant_read_write_data(get_subscriptions_lambda)

        subscriptions_api_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(get_subscriptions_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )


