from rest_framework.views import APIView
from .serilazers import *
from .models import *
from rest_framework import status
from rest_framework.response import Response
import random, string
from datetime import timedelta
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings


class UserRegView(APIView):

    def post(self, request):
        try:
            data = request.data
            serializer = UserRegSerializer(data=data)

            if serializer.is_valid():

                user = CustomUser.objects.create_user(**serializer.validated_data)
                otp = "".join(random.choices(string.digits, k=6))
                user.otp = otp
                user.otp_expiry = timezone.now() + timedelta(minutes=5)
                user.save()

                try:
                    send_mail(
                        "Your OTP Code",
                        f"Your OTP code is {otp}",
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    return Response(
                        {"message": "User created. Please verify your OTP."},
                        status=status.HTTP_201_CREATED,
                    )

                except BadHeaderError:
                    return Response(
                        {"error": "Invalid header found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )


class VerifyOtpView(APIView):
    def post(self, request):
        try:
            print("hello world")
            data = request.data
            serializer = OtpVerificationSerializer(data=data)

            if serializer.is_valid():

                email=serializer.validated_data["email"]
                otp=serializer.validated_data["otp"]
                user = CustomUser.objects.filter(email=email).first()

                if user and user.otp == otp and user.otp_expiry > timezone.now():
                    user.otp = None
                    user.otp_expiry = None
                    user.is_active = True
                    user.save()

                return Response(
                    {"message": "account registered successfully"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"message": "Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )


class AdminRegView(APIView):

    def post(self, request):
        try:
            data = request.data
            serializer = AdminRegSerializer(data=data)
            if serializer.is_valid():

                CustomUser.objects.create_superuser(**serializer.validated_data)
                return Response(
                    {"message": "admin registered succesfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )


class CollegeRegView(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = CollegeRegSerializer(data=data)
            if serializer.is_valid():

                CustomUser.objects.create_user(**serializer.validated_data)
                return Response(
                    {"message": "college registered succesfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)

            if serializer.is_valid():

                response = serializer.get_jwt_token(serializer.data)
                return Response(response, status=status.HTTP_200_OK)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )

