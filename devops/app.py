#!/usr/bin/env python3

from aws_cdk import core

from osiris_stack import OsirisStack

app = core.App()

OsirisStack(app, id="osiris-dev", env={'region': 'us-east-1'})

app.synth()
