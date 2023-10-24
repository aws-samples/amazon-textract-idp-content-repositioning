## **Part 1 - Workflow**

## Solution Architecture

![Textract-TL_Textract_Part_1](https://github.com/aws-samples/amazon-textract-idp-content-repositioning/assets/32926625/b3e72e2e-9c60-4d90-8a3e-62d426578eda)

**Workflow**

1. Uploaded a image with content File on S3 Bucket
2. On Completions of upload on S3 triggers a notification and sends message on SQS. 
3. Once SQS receives the message, it create a queue and trigger the Lambda. 
4. Lambda receives a sample payload which the python code process and follow the next step.
```
{
  "Records": [
    {
      "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
      "receiptHandle": "MessageReceiptHandle",
      "body": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"ap-south-1\",\"eventTime\":\"2023-06-23T03:52:49.568Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:XXXXXXXXXX:XXXXXXXX\"},\"requestParameters\":{\"sourceIPAddress\":\"xx.xx.xx.xx\"},\"responseElements\":{\"x-amz-request-id\":\"ABCDEF12345\",\"x-amz-id-2\":\"\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"SQS_NAME\",\"bucket\":{\"name\":\"bucket-name\",\"ownerIdentity\":{\"principalId\":\"XXXXXXXXXX\"},\"arn\":\"arn:aws:s3:::bucket-name\"},\"object\":{\"key\":\"folder/filename\",\"size\":393295,\"eTag\":\"74c336a816e3f23c101b96dfa17c43ba\",\"sequencer\":\"006495171172E17CBD\"}}}]}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1523232000000",
        "SenderId": "123456789012",
        "ApproximateFirstReceiveTimestamp": "1523232000001"
      },
      "messageAttributes": {},
      "md5OfBody": "{{{md5_of_body}}}",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:us-east-1:1234567890:QueueName",
      "awsRegion": "region"
    }
  ]
}
```
4. Lambda initiate Textract Client and then make a call to [start_document_text_detection](https://docs.aws.amazon.com/textract/latest/dg/API_StartDocumentTextDetection.html) to submit a async job to detect document text. In return it provide as JobId which is saved along with other metadata like filename, bucketName , start date time in dynamodb using DynamoDB client by calling [put_item](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_PutItem.html) 

5. On Sucessful execution lambda function retuen following response.
```
{
  "statusCode": 200,
  "body": "completed"
}
```


## AWS Services Used
----
- [Amazon Simple Storage Service (S3)](https://aws.amazon.com/s3/) - Object storage built to retrieve any amount of data from anywhere
- [Amazon Simple Queue Service (SQS)](https://aws.amazon.com/sqs/) - Fully managed message queuing for microservices, distributed systems, and serverless applications
- [AWS Lambda](https://aws.amazon.com/lambda/) - Run code without thinking about servers or clusters
- [Amazon Textract](https://aws.amazon.com/textract/) - Automatically extract printed text, handwriting, and data from any document
- [Amazon Simple Notification Service (SNS)](https://aws.amazon.com/sns/) - Fully managed Pub/Sub service for A2A and A2P messaging
- [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) - Fast, flexible NoSQL database service for single-digit millisecond performance at any scale
- [AWS Identity & Access Management](https://aws.amazon.com/iam/) - Securely manage identities and access to AWS services and resources

<br/>

## Prerequisite
----

1. Create an S3 bucket and Enable Event Notification to send message on SQS.
2. Configure Lambda Function Trigger (Initiator Lambda) on SQS.
3. Configure SNS Topic and Subscriptions.
4. Create IAM Role (_LAMBDA-DEMOAPP-INITIATOR_) for Initiator Lambda.
5. Create IAM Role (_SNS-TEXTRACT-DEMOAPP_) for Textract to notify SNS.
6. Create IAM Role (_LAMBDA-DEMOAPP-POSTPROCESSOR_) for Post Processor Lambda.

<br/>


## **IAM ROLES**

### LAMBDA-DEMOAPP-INITIATOR
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "dynamodb:PutItem",
                "sqs:ReceiveMessage",
                "sqs:GetQueueAttributes",
                "sqs:DeleteMessage",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:dynamodb:<region>:<account_id>:table/<dynamodb_table>",
                "arn:aws:sqs:<region>:<account_id>:<sqs>",
                "arn:aws:logs:<region>:<account_id>:log-group:/aws/lambda/*:*",
                "arn:aws:s3:::<bucket>/<folder>/*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "textract:StartDocumentTextDetection",
                "logs:CreateLogGroup"
            ],
            "Resource": "*"
        }
    ]
}
```

### SNS-TEXTRACT-DEMOAPP

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "sns:*",
            "Resource": "arn:aws:sns:<region>:<account_id>:<sns_topic>"
        }
    ]
}
```

### LAMBDA-DEMOAPP-POSTPROCESSOR

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "logs:CreateLogGroup"
            ],
            "Resource": [
                "arn:aws:dynamodb:<region>:<account_id>:table/<dynamodb_table>",
                "arn:aws:logs:<region>:<account_id>:log-group:*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:<region>:<account_id>:log-group:*:log-stream:*",
                "arn:aws:logs:<region>:<account_id>:log-group:/aws/lambda/*:*"
            ]
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "textract:GetDocumentTextDetection",
            "Resource": "*"
        }
    ]
}
```

## **Part 1 - Workflow**

1. Uploaded a image with content File on S3 Bucket
2. On Completions of upload on S3 triggers a notification and sends message on SQS. 
3. Once SQS receives the message, it create a queue and trigger the Lambda. 
4. Lambda receives a sample payload which the python code process and follow the next step.
```
{
  "Records": [
    {
      "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
      "receiptHandle": "MessageReceiptHandle",
      "body": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"ap-south-1\",\"eventTime\":\"2023-06-23T03:52:49.568Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:XXXXXXXXXX:XXXXXXXX\"},\"requestParameters\":{\"sourceIPAddress\":\"xx.xx.xx.xx\"},\"responseElements\":{\"x-amz-request-id\":\"ABCDEF12345\",\"x-amz-id-2\":\"\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"SQS_NAME\",\"bucket\":{\"name\":\"bucket-name\",\"ownerIdentity\":{\"principalId\":\"XXXXXXXXXX\"},\"arn\":\"arn:aws:s3:::bucket-name\"},\"object\":{\"key\":\"folder/filename\",\"size\":393295,\"eTag\":\"74c336a816e3f23c101b96dfa17c43ba\",\"sequencer\":\"006495171172E17CBD\"}}}]}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1523232000000",
        "SenderId": "123456789012",
        "ApproximateFirstReceiveTimestamp": "1523232000001"
      },
      "messageAttributes": {},
      "md5OfBody": "{{{md5_of_body}}}",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:us-east-1:1234567890:QueueName",
      "awsRegion": "region"
    }
  ]
}
```
4. Lambda initiate Textract Client and then make a call to [start_document_text_detection](https://docs.aws.amazon.com/textract/latest/dg/API_StartDocumentTextDetection.html) to submit a async job to detect document text. In return it provide as JobId which is saved along with other metadata like filename, bucketName , start date time in dynamodb using DynamoDB client by calling [put_item](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_PutItem.html) 

5. On Sucessful execution lambda function retuen following response.
```
{
  "statusCode": 200,
  "body": "completed"
}
```




