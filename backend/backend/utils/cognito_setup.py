from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_cognito as cognito,
    aws_lambda as _lambda
)
from constructs import Construct

def setup_cognito(stack):
    user_pool = cognito.UserPool(
        stack,
        "MusicAppUserPool",
        user_pool_name="music-app-user-pool",
        
        sign_in_aliases=cognito.SignInAliases(
            email=True,
            username=True,
        ),
        
        self_sign_up_enabled=True,
        
        standard_attributes=cognito.StandardAttributes(
            email=cognito.StandardAttribute(
                required=True,
                mutable=True,
            ),
            given_name=cognito.StandardAttribute(
                required=True,
                mutable=True,
            ),
            family_name=cognito.StandardAttribute(
                required=True,
                mutable=True,
            ),
            birthdate=cognito.StandardAttribute(
                required=True,
                mutable=True
            )
        ),

        custom_attributes={
        "role": cognito.StringAttribute(
            min_len=1,
            max_len=20,
            mutable=True
            )
        },

        password_policy=cognito.PasswordPolicy(
            min_length=6,
            require_lowercase=False,
            require_uppercase=False,
            require_digits=False,
            require_symbols=False,
        ),

        account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
        
        mfa=cognito.Mfa.OFF,
        
        removal_policy=RemovalPolicy.DESTROY,
    )

    user_pool_client = user_pool.add_client(
        "MusicStreamingApp",
        user_pool_client_name="music-streaming-client",
        generate_secret=False,

        auth_flows=cognito.AuthFlow(
            user_password=True,
            user_srp=True,
        ),
        
        access_token_validity=Duration.hours(1),
        id_token_validity=Duration.hours(1),
        refresh_token_validity=Duration.days(5),
        
        prevent_user_existence_errors=True,
        enable_token_revocation=True
    )

    CfnOutput(
        stack,
        "UserPoolId",
        value=user_pool.user_pool_id,
        description="User Pool ID",
    )

    CfnOutput(
        stack,
        "UserPoolClientId",
        value=user_pool_client.user_pool_client_id,
        description="User Pool Client ID",
    )

    pre_sign_up_lambda = _lambda.Function(
        stack,
        "PreSignUpLambda",
        runtime=_lambda.Runtime.PYTHON_3_11,
        handler="index.main",
        code=_lambda.Code.from_inline(
            """def main(event, context):
                # Auto-confirm user and auto-verify email
                event['response']['autoConfirmUser'] = True
                event['response']['autoVerifyEmail'] = True
                return event
            """
        )
    )

    user_pool.add_trigger(cognito.UserPoolOperation.PRE_SIGN_UP, pre_sign_up_lambda)

    return user_pool, user_pool_client