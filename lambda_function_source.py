import json
import boto3
client = boto3.client('glue')

def lambdat_handler(event, context):
    print("Crawler starting...")
    response = client.start_crawler(name = 's3gluecrawler')
    print(json.dumps(response))