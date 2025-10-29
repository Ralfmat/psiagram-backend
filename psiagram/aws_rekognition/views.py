import boto3
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME
)

rekognition_client = boto3.client(
    'rekognition',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME
)

class InitiateUploadView(APIView):
    """
    View to initiate an upload by generating a pre-signed S3 URL.
    """
    def post(self, request):
        try:
            # 1. Extract filename and content type from the request
            filename = request.data.get('filename')
            content_type = request.data.get('content_type')

            if not filename or not content_type:
                return Response(
                    {"error": "Filename and content_type are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. Generate a unique filename (S3 key)
            file_key = f"uploads/{uuid.uuid4()}_{filename}"

            # 3. Generate a pre-signed URL for PUT operation
            presigned_url = s3_client.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': settings.AWS_S3_BUCKET_NAME,
                    'Key': file_key,
                    'ContentType': content_type
                    # 'ACL': 'public-read' #TODO decide on ACL, it may be needed for public access
                },
                ExpiresIn=3600  # URL expiration time in seconds (1 hour)
            )

            # 4. Return the pre-signed URL and S3 key to the client
            return Response({
                "upload_url": presigned_url,
                "file_key": file_key
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error generating URL: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UploadCompleteView(APIView):
    """
    View to handle post-upload processing, such as Rekognition analysis.
    """
    def post(self, request):
        try:
            # 1. Extract the S3 key from the request
            file_key = request.data.get('file_key')

            if not file_key:
                return Response(
                    {"error": "file_key is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. Call Rekognition to analyze the image
            response = rekognition_client.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': settings.AWS_S3_BUCKET_NAME,
                        'Name': file_key
                    }
                },
                MaxLabels=10,
                MinConfidence=70
            )

            is_dog_detected = False
            for label in response.get('Labels'):
                if label['Name'] == 'Dog':
                    is_dog_detected = True
                    break
            
            # 3. Dog detected
            # TODO post photo approved, decide what to do
            if is_dog_detected:
                return Response({
                    "status": "approved",
                    "message": "Cute dog! Photo accepted.",
                    "labels": response.get('Labels')
                }, status=status.HTTP_200_OK)
            else:
                s3_client.delete_object(
                    Bucket=settings.AWS_S3_BUCKET_NAME,
                    Key=file_key
                )
                return Response({
                    "status": "rejected",
                    "message": "No dog detected :( Photo rejected.",
                    "labels": response.get('Labels')
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            #TODO there might be a need to handle specific exceptions like file not found in S3
            return Response(
                {"error": f"Error processing upload: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
