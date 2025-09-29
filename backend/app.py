#!/usr/bin/env python3

import aws_cdk as cdk

from backend.backend_stack import BackendStack


app = cdk.App()

account = app.node.try_get_context("myapp:account")
region = app.node.try_get_context("myapp:region")

BackendStack(app, "BackendStack", env=cdk.Environment(account=account, region=region))

app.synth()
