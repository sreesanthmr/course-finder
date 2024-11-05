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
        # email = data.get('email')
        # password = data.get('password')
        # student_name = data.get('student_name')
        # gender = data.get('gender')
        # location = data.get('location')
        try:
            # print("hi")
            custom_user_data = {
                "email": request.data.get("email"),
                "password": request.data.get("password"),
                # "name": request.data.get("name"),
            }

            # print("world")
            serializer_one = CustomUserSerializer(data=custom_user_data)

            # print("hello")
            if serializer_one.is_valid():
                # print("hhhhh")
                user = CustomUser.objects.create_user(**serializer_one.validated_data)
                # print(type(user))

            else:
                print("Serializer one errors:", serializer_one.errors)
                return Response(
                    serializer_one.errors, status=status.HTTP_400_BAD_REQUEST
                )

            student_data = {
                "student_name": request.data.get("student_name"),
                "gender": request.data.get("gender"),
                "location": request.data.get("location"),

            }

            serializer_two = StudentSerializer(data=student_data)
        

            if serializer_two.is_valid():
                student = serializer_two.save()

                student.custom_user = user
                otp = "".join(random.choices(string.digits, k=6))
                student.otp = otp
                student.otp_expiry = timezone.now() + timedelta(minutes=5)

                student.save()

                try:
                    send_mail(
                        "Your OTP Code",
                        f"Your OTP code is {otp}",
                        settings.EMAIL_HOST_USER,
                        [student.custom_user.email],
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
            else:
                print("Serializer one errors:", serializer_two.errors)
  
        except Exception as e:
            return Response(
                {"message": f"somthing went wrong========={e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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


# class CollegeRegView(APIView):
#     def post(self, request):
#         data = request.data
#         serializer = CollegeSerializer(data=data)

#         if serializer.is_valid():
#             college = serializer.save()
#             return Response(
#                 {"message": "College registered successfully. Please log in to receive your token."},
#                 status=status.HTTP_201_CREATED,
#             )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminRegView(APIView):
    def post(self, request):
        data = request.data
        serializer = AdminRegSerializer(data=data)

        if serializer.is_valid():
            admin = CustomUser.objects.create_superuser(**serializer.validated_data)
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
