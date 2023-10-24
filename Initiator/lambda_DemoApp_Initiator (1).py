# lambda function to trigger the textract job for the given document
# this lambda function is triggered by the s3 event trigger in the s3 bucket

# Lambda Environment Variables
# DYANMODB_TABLE_NAME
# SNSTOPIC_ARN
# SNSROLE_ARN


import json
import boto3
from datetime import datetime
import os

textract_client = boto3.client("textract")

# Get Enviornment Variables
dynamodb_table_name = os.environ['DYANMODB_TABLE_NAME']
sns_topic_arn = os.environ['SNSTOPIC_ARN']
snsrole_arn = os.environ['SNSROLE_ARN']
print(dynamodb_table_name, sns_topic_arn, snsrole_arn)

def lambda_handler(event, context):
    payloadBody = json.loads(event['Records'][0]['body'])
    # Initiating start_document_text_detection
    try:
        bucket = payloadBody['Records'][0]['s3']['bucket']['name']
        key = payloadBody['Records'][0]['s3']['object']['key']
        
        print(bucket, key)
        response = textract_client.start_document_text_detection(
                    DocumentLocation={
                        'S3Object': {
                            'Bucket': bucket,
                            'Name': key,
                        }
                    },
                    NotificationChannel={
                        'SNSTopicArn': sns_topic_arn,
                        'RoleArn': snsrole_arn
                    }
                )
                
        print(response)

        # Save the job id and file metadata in dynamodb
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(dynamodb_table_name)
        table.put_item(
            Item={
                'JobId': response['JobId'],
                'Bucket': bucket,
                'Key': key,
                'CreatedAt': str(datetime.now())
                }
                )
        
    except Exception as e:
        print(e)
    
    return {
        'statusCode': 200,
        'body': json.dumps('completed')
    }