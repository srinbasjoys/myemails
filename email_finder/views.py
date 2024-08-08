import asyncio
import requests
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import EmailVerificationResult
from .serializers import EmailVerificationResultSerializer, EmailFinderInputSerializer
from django.db import IntegrityError

class EmailFinderView(APIView):
    
    def post(self, request):
        input_serializer = EmailFinderInputSerializer(data=request.data)
        if input_serializer.is_valid():
            fname = input_serializer.validated_data['fname']
            lname = input_serializer.validated_data['lname']
            domain = input_serializer.validated_data['domain']

            # Define a list of email patterns to try
            email_patterns = [
                f"{fname}.{lname}@{domain}",  # First.Last@Domain
                f"{fname[0]}{lname}@{domain}",  # FirstInitialLast@Domain
                f"{fname}@{domain}",  # First@Domain
                f"{lname}.{fname}@{domain}",  # Last.First@Domain
                f"{lname[0]}{fname}@{domain}"  # LastInitialFirst@Domain
            ]

            valid_email = None  # Initialize valid_email to None

            # Process the email verification asynchronously
            for email in email_patterns:
                if valid_email:
                    print(valid_email)
                    break  # Stop checking other patterns if a valid email is found
                if asyncio.run(self.verify_email_async(email)):
                    valid_email = email  # Set valid_email if a valid email is found

            if valid_email:
                try:
                    # Save the verification result to the database
                    result_instance = EmailVerificationResult(email=valid_email, verification_status='Valid')
                    result_instance.save()
                    return Response({'message': 'Email is valid', 'valid_email': valid_email}, status=200)
                except IntegrityError:
                    # Handle the case where a duplicate email is detected
                    return Response({'message': 'Email already exists in the database', 'valid_email': valid_email}, status=409)
            else:
                return Response({'message': 'No valid email found'}, status=404)
        else:
            return Response(input_serializer.errors, status=400)

    async def verify_email_async(self, email):
        # Perform email verification
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
            is_valid = data.get('is_reachable') == 'safe' or data.get('is_reachable') == 'risky'
            return is_valid
        else:
            print(f"Email: {email}, Verification Status: Email verification failed")
            return False

    def get(self, request):
        # Handle GET requests here, e.g., for retrieving data or other operations
        return Response({'message': 'GET request is not supported for this endpoint'}, status=405)
