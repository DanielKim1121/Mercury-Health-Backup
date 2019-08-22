from __future__ import print_function
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

# MODIFY
USER_POOL_ID = 'us-west-2_mHjkrzq4P'
CLIENT_ID = '6114cq3h77t64kovjdo5h2v8n9'
CLIENT_SECRET = ' '
client = None

ERROR = 0
SUCCESS = 1
USER_EXISTS = 2

def sign_up(username, name, password):
    try:
        resp = client.sign_up(
            ClientId=CLIENT_ID,
            Password = password,
            Username = username,
            UserAttributes=[
                {
                    'Name': 'name',
                    'Value': name
                },
            ],

            )
    except client.exceptions.UsernameExistsException as e:
        return USER_EXISTS
    except Exception as e:
        return ERROR
    return SUCCESS

def logout(username):
    try:
        resp = client.admin_user_global_sign_out(
            UserPoolId=USER_POOL_ID,
            Username=username
            )
        print(resp)
    except Exception as e:
        print(e)
        return ERROR
    return SUCCESS

def forgot_password(username):
    try:
        resp = client.forgot_password(
            ClientId=CLIENT_ID,
            Username=username
            )
        print(resp)
    except Exception as e:
        print(e)
        return ERROR
    return SUCCESS

def confirm_forgot_password(username, confirmationCode, newPassword):
    try:
        resp = client.confirm_forgot_password(
            ClientId=CLIENT_ID,
            Username= username,
            ConfirmationCode=confirmationCode,
            Password= newPassword
        )
        print(resp)
    except Exception as e:
        print(e)
        return ERROR
    return SUCCESS

def initiate_auth(username, password):
    try:
        resp = client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            },
            ClientMetadata={
                'username': username,
                'password': password
            })
    except client.exceptions.NotAuthorizedException as e:
        return None, "The username or password is incorrect"
    except Exception as e:
        print(e)
        return None, e
    return resp, None



def get_expire_time(RefreshToken):
    try:
        resp = client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow='REFRESH_TOKEN',
            AuthParameters={
                'REFRESH_TOKEN': RefreshToken,
            })
    except client.exceptions.NotAuthorizedException as e:
        return None, "not authorized to perform this function"
    except Exception as e:
        print(e)
        return None, "Token is wrong"
    return resp, None



def lambda_handler(event, context):
    global client
    if client == None:
        client = boto3.client('cognito-idp')

    print(event)
    body = event
    is_new = "false"

    if event['process'] == 'register':
        email = body['email']
        name = body['name']
        password = body['password']
        DevID = body['DevID']
        user_id = str(uuid.uuid4())
        signed_up = sign_up(email, name, password)
        if signed_up == ERROR:
            return {'status': 'fail', 'msg': 'failed to sign up'}
        if signed_up == USER_EXISTS:
             return {'status': 'fail', 'msg': 'user already exists'}
        if signed_up == SUCCESS:
            contactTable = boto3.resource('dynamodb').Table('MercuryHealthUserInfo')
            contactData = {
        		'Username': email,
        		'EmergencyContactInfo': "not set",
        		'DevID':DevID,
        	}
            contactTable.put_item(Item=contactData)
            is_new = "true"
            #user_id = str(uuid.uuid4())
        return {'status': 'Success'}

    elif event['process'] == 'authenticate':
        password = body['password']
        username = body['email']
        resp, msg = initiate_auth(username, password)
        if msg != None:
            return {'status': 'fail', 'msg': msg, 'error': "username or password is not correct"}
        id_token = resp['AuthenticationResult']['IdToken']
        RefreshToken = resp['AuthenticationResult']['RefreshToken']
        AccessToken = resp['AuthenticationResult']['AccessToken']
        print(RefreshToken)
        '''contactTable = boto3.resource('dynamodb').Table('MercuryHealthUserInfo')
        try:
            response = contactTable.get_item(
				Key={
					'Username': username
				}
			)
        except ClientError as e:
            return {'status': 'fail', 'msg': e}
        devTable = boto3.resource('dynamodb').Table('DeviceInfo')
        devData = {
            'DevID': response['Item']['DevID'],
            'IdToken': id_token,
            'AccessToken':AccessToken,
            'RefreshToken':RefreshToken
        }
        devTable.put_item(Item=devData)'''
        return {'status': 'Success', 'id_token': id_token, 'RefreshToken': RefreshToken, 'is_new': is_new, 'AccessToken': AccessToken}

    elif event['process'] == 'get_new_token':
        RefreshToken = body['RefreshToken']
        resp, msg = get_expire_time(RefreshToken)
        if msg != None:
            return {'status': 'fail', 'msg': msg}
        id_token = resp['AuthenticationResult']['IdToken']
        AccessToken = resp['AuthenticationResult']['AccessToken']
        ExpiresIn = resp['AuthenticationResult']['ExpiresIn']
        return {'status': 'Success', 'id_token': id_token, 'AccessToken': AccessToken, 'ExpiresIn':ExpiresIn}

    elif event['process'] == 'logout':
        username = body['email']
        resp = logout(username)
        if resp == ERROR:
            return {'status': 'fail', 'msg': 'failed to logout'}
        if resp == SUCCESS:
            return {'status': 'Success'}

    elif event['process'] == 'forgot_password':
        username = body['email']
        resp = forgot_password(username)
        if resp == ERROR:
            return {'status': 'fail', 'msg': 'failed to send the forgot password message'}
        if resp == SUCCESS:
            return {'status': 'Success'}

    elif event['process'] == 'confirm_forgot_password':
        username = body['email']
        confirmationCode = body['confirmationCode']
        newPassword = body['newPassword']
        resp = confirm_forgot_password(username, confirmationCode, newPassword)
        if resp == ERROR:
            return {'status': 'fail', 'msg': 'failed to confirm forgot password'}
        if resp == SUCCESS:
            return {'status': 'Success'}

    return {'status': 'fail', 'msg': 'failed to perform the process'}

 
