# lambda function to process textract job
# this lambda trigger by sns

# Lambda Environment Variables
# DYANMODB_TABLE_NAME

import json
import boto3
from datetime import datetime
import os

textract_client = boto3.client("textract")

# Get Enviornment Variables
dynamodb_table_name = os.environ['DYANMODB_TABLE_NAME']


def lambda_handler(event, context):
    print(event['Records'][0]['Sns'])
    payloadBody = json.loads(event['Records'][0]['Sns']['Message'])
    job_id =  payloadBody['JobId']
    collection_of_textract_responses = get_text_results_from_textract(job_id=job_id)
    total_text_with_info, font_sizes_and_line_numbers = get_the_text_with_required_info(collection_of_textract_responses)
    responsePG = paragraphs_detection(total_text_with_info)
    responseHeading = headings(total_text_with_info)
    
    print(responsePG)
    print(responseHeading)

    # update dynamodb by JobId key
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamodb_table_name)
    dbResponse = table.get_item(Key={'JobId': job_id})
    currentItem = dbResponse['Item']
    currentItem['paragraphs'] = responsePG
    currentItem['headings'] = json.dumps(responseHeading)
    currentItem['UpdatedAt'] = str(datetime.now())
    table.put_item(Item=currentItem)
    
    return {
        'statusCode': 200,
        'body': json.dumps(responsePG)
    }


def get_text_results_from_textract(job_id):
    response = textract_client.get_document_text_detection(JobId=job_id)
    collection_of_textract_responses = []
    pages = [response]

    collection_of_textract_responses.append(response)

    while 'NextToken' in response:
        next_token = response['NextToken']
        response = textract_client.get_document_text_detection(
            JobId=job_id, NextToken=next_token)
        pages.append(response)
        collection_of_textract_responses.append(response)
    return collection_of_textract_responses

def get_the_text_with_required_info(collection_of_textract_responses):
    total_text = []
    total_text_with_info = []
    running_sequence_number = 0

    font_sizes_and_line_numbers = {}
    for page in collection_of_textract_responses:
        per_page_text = []
        blocks = page['Blocks']
        for block in blocks:
            if block['BlockType'] == 'LINE':
                block_text_dict = {}
                running_sequence_number += 1
                block_text_dict.update(text=block['Text'])
                block_text_dict.update(page=block['Page'])
                block_text_dict.update(left_indent=round(
                    block['Geometry']['BoundingBox']['Left'], 2))
                font_height = round(
                    block['Geometry']['BoundingBox']['Height'], 3)
                line_number = running_sequence_number
                block_text_dict.update(font_height=round(
                    block['Geometry']['BoundingBox']['Height'], 3))
                block_text_dict.update(indent_from_top=round(
                    block['Geometry']['BoundingBox']['Top'], 2))
                block_text_dict.update(text_width=round(
                    block['Geometry']['BoundingBox']['Width'], 2))
                block_text_dict.update(line_number=running_sequence_number)

                if font_height in font_sizes_and_line_numbers:
                    line_numbers = font_sizes_and_line_numbers[font_height]
                    line_numbers.append(line_number)
                    font_sizes_and_line_numbers[font_height] = line_numbers
                else:
                    line_numbers = []
                    line_numbers.append(line_number)
                    font_sizes_and_line_numbers[font_height] = line_numbers

                total_text.append(block['Text'])
                per_page_text.append(block['Text'])
                total_text_with_info.append(block_text_dict)

    return total_text_with_info, font_sizes_and_line_numbers

def get_text_with_line_spacing_info(total_text_with_info):
    i = 1
    text_info_with_line_spacing_info = []
    while (i < len(total_text_with_info) - 1):
        previous_line_info = total_text_with_info[i - 1]
        current_line_info = total_text_with_info[i]
        next_line_info = total_text_with_info[i + 1]
        if current_line_info['page'] == next_line_info['page'] and previous_line_info['page'] == current_line_info['page']:
            line_spacing_after = round((next_line_info['indent_from_top'] - current_line_info['indent_from_top']), 2)
            spacing_with_prev = round((current_line_info['indent_from_top'] - previous_line_info['indent_from_top']), 2)
            current_line_info.update(line_space_before=spacing_with_prev)
            current_line_info.update(line_space_after=line_spacing_after)
            text_info_with_line_spacing_info.append(current_line_info)
        else:
            text_info_with_line_spacing_info.append(None)
        i += 1
    return text_info_with_line_spacing_info

def extract_paragraphs_only(data):
    paras = []
    i = 0
    paragraph_data = []
    while i < len(data):
        line = data[i]
        if line:
            if line['line_space_before'] > line['line_space_after']:
                paras.append(''.join(paragraph_data))
                paragraph_data = []
                paragraph_data.append(line['text'])
                if i < len(data)-1:
                    next_line = data[i + 1]
                    if next_line and line['text_width'] > next_line['text_width']/2:
                        paragraph_data.append(next_line['text'])
                        i += 1
                    else:
                        paras.append(' '.join(paragraph_data))
                        paragraph_data = []
            else:
                paragraph_data.append(line['text'])
        i += 1
    return paras

def paragraphs_detection(metadata):
    current = 0
    initial_data = metadata[current]
    blocks = []
    visited = []
    paragraph_output = []

    for i in range(0, len(metadata)-1):
        print("========PD Start============")
        print(metadata[i])
        block = [metadata[i]["text"]]
        last_match = i
        if metadata[i] not in visited:
            for j in range(i+1, len(metadata)):
                if metadata[j] not in visited:
                    if ((abs(float(metadata[last_match]["left_indent"] - float(metadata[j]["left_indent"]))) < 0.15) and (abs(float(metadata[last_match]["indent_from_top"] - float(metadata[j]["indent_from_top"]))) < 0.15)):
                        block.append(metadata[j]["text"])
                        last_match = j
                        visited.append(metadata[j])
            blocks.append(block)
        else:
            pass

        visited.append(metadata[i])
        print("========PD End============")

    
    for i in blocks:
        paragraph_output.append(i)

    return paragraph_output

def headings(total_text_with_info):
    list_of_headings = [
        i for i in total_text_with_info if (i["font_height"] > 0.025)]

    headings = {}
    for i in list_of_headings:
        if (i["page"] not in headings.keys()):
            headings[i["page"]] = (i["text"], i["line_number"])
        else:
            headings[i["page"]] = (
                headings[i["page"]][0] + i["text"], i["line_number"])

    return headings