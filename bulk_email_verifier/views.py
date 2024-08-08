import uuid
import os
import chardet
import requests
from django.http import JsonResponse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from rest_framework import generics, status
from concurrent.futures import ThreadPoolExecutor
from .models import BulkEmailVerification
from .serializers import BulkEmailVerificationSerializer
import pandas as pd
import time

class BulkEmailVerificationCreateView(generics.CreateAPIView):
    queryset = BulkEmailVerification.objects.all()
    serializer_class = BulkEmailVerificationSerializer

    def perform_create(self, serializer):
        file = serializer.validated_data.get('file')

        if not file:
            raise ValidationError("File not provided.")

        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())

        # Save the file with the generated ID as the filename
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        file_path = os.path.join('uploads', file_id)
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        with fs.open(full_file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        download_url = self.verify_emails(full_file_path, file_id)

        if download_url:
            serializer.save(download_url=download_url, file_id=file_id)
            return JsonResponse({'download_url': download_url}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({'error': 'File not found'}, status=status.HTTP_400_BAD_REQUEST)

    def verify_emails(self, full_file_path, file_id):
        try:
            # Use chardet to detect the file's encoding
            with open(full_file_path, 'rb') as rawdata:
                result = chardet.detect(rawdata.read())
            detected_encoding = result['encoding']

            # Read the file with the detected encoding using pandas
            df = pd.read_csv(full_file_path, encoding=detected_encoding)
            df = pd.DataFrame(df)

            results = []

            # Add your email pattern generation logic here
            email_list = df['Email'].tolist()

            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(self.verify_email, email_list))

            # Create a DataFrame with results
            results_df = pd.DataFrame(list(zip(email_list, results)), columns=['Email', 'Status'])

            # Write the results to a CSV file using pandas
            result_file_name = f'{file_id}_results.csv'
            result_file = os.path.join(settings.MEDIA_ROOT, result_file_name)
            results_df.to_csv(result_file, index=False)

            results_url = os.path.join(settings.MEDIA_URL, result_file_name)
            return results_url

        except FileNotFoundError:
            return JsonResponse({'error': 'File not found'}, status=status.HTTP_400_BAD_REQUEST)

    def verify_email(self, email):
        try:
            verification_url="https://apilayer.net/api/check?access_key=08bb0884cdf3e57bbe4b3c8504389e43&email=email"
            verification_url = 'http://192.99.229.66:8080/v0/check_email'
            payload = {"to_email": email}
            headers = {
                "Authorization": "",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = requests.post(verification_url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                is_valid = data.get('is_reachable') in ['safe']
                print(f"Email: {email}, Verification Status: {'Valid' if is_valid else 'Invalid'}")
                return 'Valid' if is_valid else 'Invalid'
            else:
                print(f"Email: {email}, Verification Status: Email verification failed")
                return 'Invalid'
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            time.sleep(5)			
            return 'Invalid'
        except Exception as e:
            print(f"Error verifying email: {e}")
            time.sleep(5)
            return 'Invalid'
