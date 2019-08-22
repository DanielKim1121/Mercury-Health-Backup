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
	UserID, msg = get_user(event['AccessToken'])
	print(UserID)
	if msg != None:
		return {'status': 'fail', 'msg': msg}
	analyticsTable = boto3.resource('dynamodb').Table('Device-User-Analytics')
	try:
		response = analyticsTable.get_item(
			Key={
				'UserID': UserID
			}
		)
	except ClientError as e:
		return {'status': 'fail', 'msg': e}
	if method == 'GET':
		if 'Item' in response:
			userAnalytics =  (response['Item']['situp']).split(' , ')
			userDataList = []
			for i in userAnalytics:
				userDatas = i.split('|')
				userDataList.append(userDatas)
			return {'status': 'Success', 'userData':response['Item']['situp']}
		else:
			return {'status': 'fail'}
	try:
	    situp = event['situp']
	    timestamp = str(datetime.utcnow())
	except KeyError:
		return {'status': 'fail', 'msg': KeyError}

	analyticsTable = boto3.resource('dynamodb').Table('Device-User-Analytics')
	analyticsListTable = boto3.resource('dynamodb').Table('Analytics-List')
	prevSitup = ""
	if 'Item' in response:
		prevSitup = response['Item']['situp']
	#create a new db entry
	analyticsData = {
		'UserID': UserID,
		'situp': prevSitup + " , " + timestamp
	}
	analyticsListData = {
		'userID': UserID,
		'timestamp': timestamp,
		'position': event['position']
	}
	try:
	    analyticsTable.put_item(Item=analyticsData)
	    analyticsListTable.put_item(Item=analyticsListData)
	except Exception as e:
	    print(e)
	    return {'status': 'fail', 'msg': e}
	return {'status': 'Success'}
	
