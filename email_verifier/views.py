import requests
from datetime import datetime, timedelta
from rest_framework import generics, status
from rest_framework.response import Response
from .models import EmailVerification
from .serializers import EmailVerificationSerializer

from .models import EmailVerification


class EmailVerificationListCreateView(generics.ListCreateAPIView):
    queryset = EmailVerification.objects.all()
    serializer_class = EmailVerificationSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
         # Replace with your actual API key

        # Check if a verification record exists for the email in the last 3 months
        three_months_ago = datetime.now() - timedelta(days=90)
        email_verification = EmailVerification.objects.filter(email=email, created_at__gte=three_months_ago).first()

        if email_verification:
            serializer = EmailVerificationSerializer(email_verification)
            if serializer.data['is_valid'] is True:
                return Response (f"Email:" + serializer.data['email'] + f", Verification Status: {'Valid'}", status=status.HTTP_200_OK)
            else:
                return Response (f"Email:" + serializer.data['email'] + f", Verification Status: {'InValid'}", status=status.HTTP_200_OK)
        else:
            # Perform email verification
            verification_url="https://apilayer.net/api/check?access_key=08bb0884cdf3e57bbe4b3c8504389e43&email=email"
            verification_url = f'http://192.99.229.66:8080/v0/check_email'
            payload = {"to_email": email}
            headers = {
                "Authorization": "",
                "Content-Type": "application/json",
                "Accept": "application/json"}
            response = requests.post(verification_url, json=payload, headers=headers)


            if response.status_code == 200:
                data = response.json()
                is_valid = data.get('is_reachable') == 'safe'
                email_verification = EmailVerification(email=email, is_valid=is_valid, response_data=data)
                email_verification.save()
                serializer = EmailVerificationSerializer(email_verification)
                print(data)
                return Response(f"Email: {email}, Verification Status: {'Valid' if is_valid else 'Invalid'}", status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Email verification failed'}, status=status.HTTP_400_BAD_REQUEST)
