from rest_framework.views import APIView
from .serilazers import *
from .models import *
from rest_framework import status
from rest_framework.response import Response
import random, string
from datetime import timedelta
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils import timezone


class StudentRegView(APIView):
    def post(self, request):
        # data = request.data

        custom_user_data = {
            "email": request.data.get("email"),
            "password": request.data.get("password"),
        }
        student_data = {
            "name": request.data.get("name"),
            "gender": request.data.get("gender"),
            "location": request.data.get("location"),
        }

        serializer_one = CustomUserSerializer(data=custom_user_data)
        serializer_two = StudentSerializer(data=student_data)

        if serializer_one.is_valid() and serializer_two.is_valid():
            user = CustomUser.objects.create_user(**serializer_one.validated_data)
            student = Student.objects.update_or_create(**serializer_two.validated_data)
            student.custom_user_id = user

            otp = "".join(random.choices(string.digits, k=6))
            student.otp = otp
            student.otp_expiry = timezone.now() + timedelta(minutes=5)
            # user.is_active = False
            student.save()

            try:
                send_mail(
                    "Your OTP Code",
                    f"Your OTP code is {otp}",
                    settings.EMAIL_HOST_USER,
                    [student.email],
                    fail_silently=False,
                )
                return Response(
                    {"message": "Student created. Please verify your OTP."},
                    status=status.HTTP_201_CREATED,
                )

            except BadHeaderError:
                return Response(
                    {"error": "Invalid header found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer_one.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    def post(self, request):
        data = request.data
        serializer = OtpVerificationSerializer(data=data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]
            student = Student.objects.filter(email=email).first()

            if student and student.otp == otp and student.otp_expiry > timezone.now():
                student.otp = None
                student.otp_expiry = None
                student.is_active = True
                student.save()
                return Response(
                    {"message": "Account verified successfully."},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"message": "Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollegeRegView(APIView):
    def post(self, request):
        data = request.data
        serializer = CollegeSerializer(data=data)

        if serializer.is_valid():
            college = serializer.save()
            return Response(
                {"message": "College registered successfully. Please log in to receive your token."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminRegView(APIView):
    def post(self, request):
        data = request.data
        serializer = AdminRegSerializer(data=data)

        if serializer.is_valid():
            admin = serializer.save()
            return Response(
                {"message": "Admin registered successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = serializer.get_jwt_token(user)
            return Response(token, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
