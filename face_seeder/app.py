from __future__ import print_function

import boto3
from decimal import Decimal
import json
import os
import urllib

print('Loading function')

def get_ssm_config( param_name ):
    config = {}
    param_details = ssm.get_parameter(Name=param_name, WithDecryption=True)
    print(param_details)
    if 'Parameter' in param_details and len(param_details.get('Parameter')) > 0:
            param = param_details['Parameter']
            config = json.loads(param['Value'])
    return config

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
ssm         = boto3.client('ssm')

config = get_ssm_config(os.environ['CONFIG_PARAM'])

REKOGNITION_DB_TBL  = os.environ['REKOGNITION_DB_TBL']  # DynamoDB Table that Stores hashes to family member names

# --------------- Helper Functions ------------------

def index_faces(bucket, key):

    response = rekognition.index_faces(
        Image={"S3Object":
            {"Bucket": bucket,
            "Name": key}},
            QualityFilter="AUTO",
            CollectionId=config['collection'])
    return response
    
def update_index(tableName,faceId, fullName):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            'RekognitionId': {'S': faceId},
            'FullName': {'S': fullName}
            }
        ) 
    
# --------------- Main handler ------------------

def lambda_handler(event, context):

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:

        # Calls Amazon Rekognition IndexFaces API to detect faces in S3 object 
        # to index faces into specified collection
        
        response = index_faces(bucket, key)
        
        # Commit faceId and full name object metadata to DynamoDB
        print(response)
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200 and len(response['FaceRecords']) > 0:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            
            print(bucket)
            print(key)
            #fullName = key[:key.find("/")]
            ret = s3.head_object(Bucket=bucket,Key=key)
            print(ret)
            personFullName = ret['Metadata']['fullname']
            print(personFullName)
            update_index(REKOGNITION_DB_TBL,faceId,personFullName)

        # Print response to console
        print(response)

        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket))
        raise e