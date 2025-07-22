import boto3
import json
import urllib.parse

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

# Load care tips from the packaged JSON file
with open("plant_care.json") as f:
    care_data = json.load(f)

def lambda_handler(event, context):
    print("EVENT:", event)

    # Get bucket and object key
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])

    # Get the image file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    # Detect labels in the image
    labels = rekognition.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=5)
    detected = [label['Name'].lower() for label in labels['Labels']]
    print("DETECTED LABELS:", detected)

    # Try to find a care tip match
    for name in detected:
        if name in care_data:
            result = {
                'statusCode': 200,
                'body': json.dumps({
                    'plant': name,
                    'care': care_data[name]
                })
            }
            print("MATCH FOUND:", result)
            return result

    # No match found
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'No plant match found',
            'detected': detected
        })
    }
