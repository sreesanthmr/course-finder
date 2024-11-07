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
from .permissions import IsAuthenticatedWithJWT


class StudentRegView(APIView):
    def post(self, request):

        try:
            custom_user_data = {
                "email": request.data.get("email"),
                "password": request.data.get("password"),
            }

            serializer_one = CustomUserSerializer(data=custom_user_data)

            if serializer_one.is_valid():
                user = serializer_one.save()

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

            serializer_two = StudentRegSerializer(data=student_data)
        

            if serializer_two.is_valid():
                student = serializer_two.save()

                student.user = user
                otp = "".join(random.choices(string.digits, k=6))
                student.otp = otp
                student.otp_expiry = timezone.now() + timedelta(minutes=5)

                student.save()


                try:
                    send_mail(
                        "Your OTP Code",
                        f"Your OTP code is {otp}",
                        settings.EMAIL_HOST_USER,
                        [student.user.email],
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
                return Response(
                    serializer_one.errors, status=status.HTTP_400_BAD_REQUEST
                )

  
        except Exception as e:
            return Response(
                {"message": f"somthing went wrong,{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyOtpView(APIView):
    def post(self, request):
        data = request.data
        serializer = OtpVerificationSerializer(data=data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]

            try:
                user = CustomUser.objects.filter(email=email).first()
            except CustomUser.DoesNotExist:
                return Response({"message": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                student = Student.objects.get(user=user)
            except Student.DoesNotExist:
                return Response({"detail": "Student data not found for this user."}, status=status.HTTP_400_BAD_REQUEST)

            if student and student.otp == otp and student.otp_expiry > timezone.now():
                student.otp = None
                student.otp_expiry = None
                user.is_active = True
                user.save()
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

        try:
            custom_user_data = {
                "email": request.data.get("email"),
                "password": request.data.get("password"),
            }
            serializer_one = CustomUserSerializer(data=custom_user_data)

            if serializer_one.is_valid():
                user = serializer_one.save()

            else:
                print("Serializer one errors:", serializer_one.errors)
                return Response(
                    serializer_one.errors, status=status.HTTP_400_BAD_REQUEST
                )
            
            college_data = {
                "college_name": request.data.get("college_name"),
                "courses": request.data.get("courses"),
                "location": request.data.get("location"),

            }
            serializer_two = CollegeRegSerializer(data=college_data)


            if serializer_two.is_valid():
                college = serializer_two.save()
                college.user = user
                college.save()

                return Response(
                    {"message": "College registered successfully. Wait for approval from admin"},
                    status=status.HTTP_201_CREATED,
                )
                
            
            else:
                print("Serializer two errors:", serializer_two.errors)
                return Response(
                    serializer_two.errors, status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            return Response(
                {"message": f"somthing went wrong,{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )



class AdminRegView(APIView):
    def post(self, request):
        data = request.data
        serializer = AdminRegSerializer(data=data)

        if serializer.is_valid():
            CustomUser.objects.create_superuser(**serializer.validated_data)
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
    
    

class LocationRegView(APIView):
    def post(self, request):
        data = request.data
        serializer = LocationSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Location registered successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CourseRegView(APIView):
    def post(self, request):
        data = request.data
        serializer = CourseSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Course registered successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class AdminCollegeApprovalView(APIView):
    def get(self, request):
        colleges = College.objects.filter(is_approved=False, approval_request_sent=True)
        
        college_data = [{"college_name": college.college_name, "location": college.location, "id": college.id} for college in colleges]
        
        return Response(college_data, status=status.HTTP_200_OK)

    def post(self, request):
        college_id = request.data.get("college_id")
        action = request.data.get("action")  

        if not college_id or action not in ['approve', 'reject']:
            return Response({"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            college = College.objects.get(id=college_id)
            user = college.user

            if action == "approve":
                college.is_approved = True
                college.approval_request_sent = False 
                user.is_active = True 
                college.save()
                user.save()
                return Response({"message": "College approved successfully."}, status=status.HTTP_200_OK)

            elif action == "reject":
                college.approval_request_sent = False  
                college.save()
                return Response({"message": "College registration rejected."}, status=status.HTTP_200_OK)

        except College.DoesNotExist:
            return Response({"message": "College not found."}, status=status.HTTP_404_NOT_FOUND)



####################################################################


class CollegeListView(APIView):
    def get(self, request):
        colleges = College.objects.all()  
        serializer = CollegeListSerializer(colleges, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)