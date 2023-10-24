# Textract Content Repositioning

## Features
An approach to extract and reposition text from images for meaningful content involves utilizing power of AWS services. This serverless streamlined process ensures accurate text extraction, followed by intelligent contextual analysis and arrangement. The solution can seamlessly extract pertinent information from images and dynamically position it in a coherent context, enhancing the overall usability and relevance of the extracted content. 

<br/>

## Solution Overview

[image]

<br/>

## Solution Workflow

The Solution workflow contains the following steps.

<br/>

#### **Part-1 Content Pipeline trigger job to process images**

    The first part of the solution get the image with content in S3, trigger the textract job and save the metadata in dynamoDB.

<br/>

#### **Part-2 Validate the processed output and reposition to provide contextual data**

    The second part trigger when the textract job gets completed, reposition the content and save it back to the database.

<br/>

**Prerequisites**

For this sample, you should have the following prerequisites.
<br/>

<a href="https://docs.aws.amazon.com/accounts/latest/reference/accounts-welcome.html">An AWS account</a> with access to the following services and follow the solution presented in this blog post.

- [Amazon Simple Storage Service (S3)](https://aws.amazon.com/s3/)
- [Amazon Simple Queue Service (SQS)](https://aws.amazon.com/sqs/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Amazon Textract](https://aws.amazon.com/textract/)
- [Amazon Simple Notification Service (SNS)](https://aws.amazon.com/sns/)
- [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)
- [AWS Identity & Access Management](https://aws.amazon.com/iam/)