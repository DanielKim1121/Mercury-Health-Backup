from __future__ import print_function
import json
import base64
import boto3

streamName = 'KinesisStream'
streamARN = 'arn:aws:kinesisvideo:us-west-2:655036945574:stream/KinesisStream/1559083770602'

def lambda_handler(event, context):
    client = boto3.client('kinesis-video-media')
    response = client.get_media(
            StreamName=streamName,
            StreamARN=streamARN,
            StartSelector={
            'StartSelectorType': 'NOW'
        })

    
