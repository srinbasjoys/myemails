import uuid
import os
import asyncio
import chardet
import requests
import concurrent.futures
from django.http import JsonResponse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from rest_framework import generics, status
from .models import BulkEmailfinder
from .serializers import BulkEmailfinderSerializer
import pandas as pd
import time

class BulkEmailfinderCreateView(generics.CreateAPIView):
    queryset = BulkEmailfinder.objects.all()
    serializer_class = BulkEmailfinderSerializer

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

        download_url = asyncio.run(self.verify_emails(full_file_path, file_id))

        if download_url:
            serializer.save(download_url=download_url, file_id=file_id)
            return JsonResponse({'download_url': download_url}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({'error': 'File not found'}, status=status.HTTP_400_BAD_REQUEST)

    async def verify_emails(self, full_file_path, file_id):
        try:
            # Use chardet to detect the file's encoding
            with open(full_file_path, 'rb') as rawdata:
                result = chardet.detect(rawdata.read())
            detected_encoding = result['encoding']
            print(detected_encoding)
            try:
                df = pd.read_csv(full_file_path, encoding='utf-8')
            except pd.errors.ParserError:
                # Handle parsing error (e.g., file contains non-decodable characters)
                return JsonResponse({'error': 'Unable to read the file. It may contain non-decodable characters.'}, status=status.HTTP_400_BAD_REQUEST)
            # Read the file with the detected encoding using pandas
            # df = pd.read_csv(full_file_path, encoding=detected_encoding)
            # df =pd.DataFrame(df)

            # Perform data cleaning and email verification using pandas
            df['FirstName'] = df['FirstName'].apply(lambda x: ''.join(filter(str.isalpha, str(x))))
            df['LastName'] = df['LastName'].apply(lambda x: ''.join(filter(str.isalpha, str(x))))
            df['Domain'] = df['Domain'].astype(str)

            results = []

            # Add your email pattern generation logic here
            with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
                loop = asyncio.get_event_loop()
                tasks = [loop.run_in_executor(executor, self.verify_email, row) for index, row in df.iterrows()]
                for is_valid, result_row in await asyncio.gather(*tasks):
                    results.append(result_row)

            # Create a DataFrame with results
            results_df = pd.DataFrame(results, columns=['fname', 'lname', 'domain', 'Emails','Verification_status'])

            # Write the results to a CSV file using pandas
            result_file_name = f'{file_id}_results.csv'
            result_file = os.path.join(settings.MEDIA_ROOT, result_file_name)
            results_df.to_csv(result_file, index=False)

            results_url = os.path.join(settings.MEDIA_URL, result_file_name)
            return results_url

        except FileNotFoundError:
            return JsonResponse({'error': 'File not found'}, status=status.HTTP_400_BAD_REQUEST)

    def verify_email(self, row):
        fname = row['FirstName']
        lname = row['LastName']
        domain = row['Domain']
        email_patterns = []

        if fname and domain:
            email_patterns.append(f"{fname}.{lname}@{domain}")
            email_patterns.append(f"{fname}@{domain}")

        if fname and lname and domain:
            email_patterns.append(f"{fname[0]}{lname}@{domain}")
            email_patterns.append(f"{fname}{lname}@{domain}")
            email_patterns.append(f"{fname}{lname[0]}@{domain}")
            email_patterns.append(f"{fname}_{lname}@{domain}")
            email_patterns.append(f"{lname}{fname[0]}@{domain}")
            email_patterns.append(f"{fname[0]}_{lname}@{domain}")
            email_patterns.append(f"{lname}_{fname[0]}@{domain}")
            email_patterns.append(f"{fname[0]}-{lname}@{domain}")
            email_patterns.append(f"{lname}-{fname[0]}@{domain}")
            email_patterns.append(f"{fname}.{lname[0]}@{domain}")
            email_patterns.append(f"{fname[0]}.{lname}@{domain}")
            email_patterns.append(f"{fname[0]}_{lname[0]}@{domain}")
            email_patterns.append(f"{fname[0]}-{lname[0]}@{domain}")
            email_patterns.append(f"{lname[0]}{fname}@{domain}")
            email_patterns.append(f"{lname}{fname[0]}@{domain}")
            email_patterns.append(f"{lname[0]}_{fname}@{domain}")
            email_patterns.append(f"{lname[0]}-{fname}@{domain}")
            email_patterns.append(f"{lname}_{fname[0]}@{domain}")
            email_patterns.append(f"{lname}-{fname[0]}@{domain}")
            email_patterns.append(f"{fname}.{lname[0]}_{domain}")
            email_patterns.append(f"{fname[0]}.{lname}_{domain}")
            email_patterns.append(f"{fname[0]}.{lname[0]}_{domain}")
            email_patterns.append(f"{fname[0]}-{lname[0]}_{domain}")
            email_patterns.append(f"{fname[0]}_{lname[0]}_{domain}")


        for email_pattern in email_patterns:
            is_valid = self.verify_email_address(email_pattern)
            if is_valid[0]:
                return is_valid, [fname, lname, domain, email_pattern,is_valid[1]]

        return False, [fname, lname, domain, '1no valid email found']

    def verify_email_address(self, email):
        try:
            verification_url="https://apilayer.net/api/check?access_key=08bb0884cdf3e57bbe4b3c8504389e43&email=email"
            verification_url = 'http://66.70.190.171:8080/v0/check_email'
            payload = {"to_email": email}
            headers = {
                "Authorization": "",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = requests.post(verification_url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                verification_status = data.get('is_reachable')
                is_valid = verification_status in ['safe', 'risky']
                if is_valid:
                    if verification_status =='safe':
                        status='valid'
                    else:
                        status='risky'
                # print(f"Email: {email}, Verification Status: {'Valid' if is_valid else 'Invalid'}")
                    return (is_valid,status)
                else:
                    print(f"Email: {email}, Verification Status: Invalid")
                    return (is_valid, verification_status)

            else:
                print(f"Email: {email}, Verification Status: Email verification failed")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            time.sleep(5)
            return False
        except Exception as e:
            print(f"Error verifying email: {e}")
            time.sleep(5)
            return False
