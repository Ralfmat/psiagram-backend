import os
import boto3
from dotenv import load_dotenv

# wczytaj .env
load_dotenv(override=True)

print("AWS_ACCESS_KEY_ID =", os.getenv("AWS_ACCESS_KEY_ID"))
print("AWS_REGION_NAME   =", os.getenv("AWS_REGION_NAME"))

rek = boto3.client(
    "rekognition",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION_NAME"),
)

try:
    # bardzo proste, „głupie” wywołanie – chodzi tylko o autoryzację
    response = rek.detect_labels(
        Image={
            "S3Object": {
                "Bucket": os.getenv("AWS_S3_BUCKET_NAME"),
                "Name": "jakis-nieistniejacy-plik.jpg",
            }
        },
        MaxLabels=1,
        MinConfidence=50,
    )
    print("UDAŁO SIĘ – odpowiedź z Rekognition:", response)
except Exception as e:
    print("BŁĄD Z REKOGNITION:", repr(e))