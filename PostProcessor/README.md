## **Part 2 - Workflow**

## Solution Overview

![Textract-TL_Textract_Part_2](https://github.com/aws-samples/amazon-textract-idp-content-repositioning/assets/32926625/1b61a366-6908-4c8d-a4e9-6f1c5fd15b97)

# **Workflow**

1. Textract Jobs will take few minutes to extract the content and on completion will send the notification to the SNS which will fan out the message to different target. In this case it will send a message on email and lambda for post processing. Here is the sample payload for notification.

```
{"JobId":"5d9bd420a3bd65d6090de7299f088dcb62cbb39d3f85b9fdc5c74cf47c8993fc","Status":"SUCCEEDED","API":"StartDocumentTextDetection","Timestamp":1693813075210,"DocumentLocation":{"S3ObjectName":"folder/filename","S3Bucket":"bucketname"}}
```

2. Once the message received by lambda it will start the post processing task where it will fetch the response from Textract service using [get_document_text_detection](https://docs.aws.amazon.com/textract/latest/dg/API_GetDocumentTextDetection.html) method. Amazon Textract returns a pagination token in the response. The pagination token has been used to retrieve the next set of blocks.

3. Once lambda fetch all records for the processed job, it calculate and reposition the content to provide a meaningful context and then update the dyanamoDB with processed data. The updation of dynamoDB is based on the JobId which is the primary key.



