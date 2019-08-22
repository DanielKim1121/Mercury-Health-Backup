import boto3
import json
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

ERROR = 0
SUCCESS = 1

def respond(err, response=None):
	return {
		'statusCode': '400' if err else '200',
		'body': err if err else json.dumps(response),
		'headers': {
			'Content-Type': 'application/json',
		},
	}

def dev_exist(DevID):
    try:
        devTable = boto3.resource('dynamodb').Table('DeviceInfo')
        response = devTable.get_item(
			Key={
				'DevID': DevID,
			}
		)
    except Exception as e:
        print(e)
        return ERROR
    return response

def put_dev_data(DevID, IP):
	try:
		devTable = boto3.resource('dynamodb').Table('DeviceInfo')
		#create a new db entry
		devData = {
			'SentOn': str(datetime.utcnow()),
			'DevID': DevID,
			'IP': IP,
		}
		devTable.put_item(Item=devData)
	except Exception as e:
		print(e)
		return ERROR
	return SUCCESS

def lambda_handler(event, context):
	if event['process'] == 'device_exist':
		DevID = event['DevID']
		print("this is working")
		resp = dev_exist(DevID)
		if resp == ERROR:
		    return {'status': 'fail', 'msg': 'DevID doesnt exist'}
		try:
			resp['Item']
		except Exception as e:
		    return {'status': 'fail', 'msg': 'DevID doesnt exist'}
		return {'status': 'Success'}

	elif event['process'] == 'put_dev_data':
		DevID = event['DevID']
		IP = event['IP']
		resp = put_dev_data(DevID, IP)
		if resp == ERROR:
		    return {'status': 'fail', 'msg': 'unknown error'}
		if resp == SUCCESS:
		    return {'status': 'Success', 'msg': 'Data was succesfully inputed'}




	return respond(None, "Good")
	
