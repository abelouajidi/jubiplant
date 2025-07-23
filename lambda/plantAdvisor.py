import boto3
import json
import urllib.parse
from difflib import get_close_matches  # pour fuzzy match optionnel

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

# Charger les données de soins
with open("plant_care.json") as f:
    care_data = json.load(f)

def lambda_handler(event, context):
    print("EVENT:", event)

    # Extraire nom du bucket et clé de l’objet
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])

    # Lire l'image depuis S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    # Appeler Rekognition avec plus de labels et un filtre de confiance
    labels = rekognition.detect_labels(
        Image={'Bytes': image_bytes},
        MaxLabels=15,
        MinConfidence=85.0
    )

    # Trier les labels par confiance décroissante
    sorted_labels = sorted(labels['Labels'], key=lambda x: x['Confidence'], reverse=True)
    detected = [label['Name'].lower() for label in sorted_labels]
    print("DETECTED LABELS:", detected)

    # Vérifier correspondance exacte
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

    # Correspondance floue (bonus)
    closest = get_close_matches(detected[0], care_data.keys(), n=1, cutoff=0.8)
    if closest:
        name = closest[0]
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'plant': name,
                'care': care_data[name],
                'match': 'fuzzy'
            })
        }
        print("FUZZY MATCH:", result)
        return result

    # Aucun match
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'No plant match found',
            'detected': detected
        })
    }
