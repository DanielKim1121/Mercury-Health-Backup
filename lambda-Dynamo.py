import boto3
import json
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

client = None




def get_user(accessToken):
    try:
        resp = client.get_user(
        	AccessToken=accessToken
        )
        print(resp)
    except Exception as e:
        print(e)
        return None, "Unknown error"
    return resp['UserAttributes'][3]['Value'], None

def lambda_handler(event, context):
	global client
	if client == None:
		client = boto3.client('cognito-idp')
	method = event['httpMethod']
	username, msg = get_user(event['AccessToken'])
	print(username)
	if msg != None:
		return {'status': 'fail', 'msg': msg}
	if method == 'GET':
		contactTable = boto3.resource('dynamodb').Table('MercuryHealthUserInfo')
		try:
			response = contactTable.get_item(
				Key={
					'Username': username
				}
			)
		except ClientError as e:
			return {'status': 'fail', 'msg': e}
		print(format(response))
		return {'status': 'Success', 'emergency_contacts': response['Item']['EmergencyContactInfo']}

	try:
		emergencyContacts = event['emergencyContacts']
	except KeyError:
		return {'status': 'fail', 'msg': KeyError}

	contactTable = boto3.resource('dynamodb').Table('MercuryHealthUserInfo')

	#create a new db entry
	contactData = {
		'Username': username,
		'EmergencyContactInfo': emergencyContacts
	}

	contactTable.put_item(Item=contactData)

	return {'status': 'Success'}
	
