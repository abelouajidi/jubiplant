import boto3
import json
import urllib.parse
import os

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

# Load care tips locally into memory
with open("/tmp/plant_care.json", "w") as f:
    f.write('{"placeholder": "This will be replaced"}')  # placeholder

def lambda_handler(event, context):
    print("EVENT:", event)
    
    # Get bucket + key
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])

    # Get image bytes from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    # Detect labels
    labels = rekognition.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=5)
    detected = [label['Name'].lower() for label in labels['Labels']]
    
    # Load care data (mock for now)
    with open("/tmp/plant_care.json") as f:
        care_data = json.load(f)

    for name in detected:
        if name in care_data:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'plant': name,
                    'care': care_data[name]
                })
            }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'No plant match found',
            'detected': detected
        })
    }

