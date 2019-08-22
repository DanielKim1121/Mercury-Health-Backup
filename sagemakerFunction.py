import json
import boto3
import numpy as np
from scipy import misc
from PIL import Image

def lambda_handler(event, context):
    test = np.zeros((245,224,3))
    test = misc.imresize(test, 256/224, interp='bilinear',)
    # TODO implement
    return {
        'statusCode': test.shape(),
        'body': json.dumps('Hello from Lambda!')
    }
