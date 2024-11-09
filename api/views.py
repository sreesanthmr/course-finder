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
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


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
                user = CustomUser.objects.filter(email=email)
            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "User with this email does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                student = Student.objects.get(user=user)
            except Student.DoesNotExist:
                return Response(
                    {"detail": "Student data not found for this user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if student and student.otp == otp and student.otp_expiry > timezone.now():
                student.otp = None
                student.otp_expiry = None
                user.is_active = True
                user.is_student = True
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
                    {
                        "message": "College registered successfully. Wait for approval from admin"
                    },
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
            user_data = serializer.validated_data.get("user_data")
            token = serializer.get_jwt_token(user)

            response_data = {
                "token": token,
                "user_data": user_data,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationRegView(APIView):
    def post(self, request):
        data = request.data
        serializer = LocationDetailsSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Location registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseRegView(APIView):
    def post(self, request):
        data = request.data
        serializer = CourseDetailsSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Course registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminCollegeApprovalView(APIView):
    def get(self, request):
        colleges = College.objects.filter(is_approved=False, approval_request_sent=True)

        college_data = [
            {
                "college_name": college.college_name,
                "location": college.location,
                "id": college.id,
            }
            for college in colleges
        ]

        return Response(college_data, status=status.HTTP_200_OK)

    def post(self, request):
        college_id = request.data.get("college_id")
        action = request.data.get("action")

        if not college_id or action not in ["approve", "reject"]:
            return Response(
                {"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            college = College.objects.get(id=college_id)
            user = college.user

            if action == "approve":
                college.is_approved = True
                college.approval_request_sent = False
                user.is_active = True
                user.is_college = True
                college.save()
                user.save()
                return Response(
                    {"message": "College approved successfully."},
                    status=status.HTTP_200_OK,
                )

            elif action == "reject":
                college.approval_request_sent = False
                college.save()
                return Response(
                    {"message": "College registration rejected."},
                    status=status.HTTP_200_OK,
                )

        except College.DoesNotExist:
            return Response(
                {"message": "College not found."}, status=status.HTTP_404_NOT_FOUND
            )


class CollegeListView(APIView):
    def get(self, request):
        permission_classes = [IsAuthenticatedWithJWT]

        try:
            colleges = College.objects.all()
            serializer = CollegeDetailsSerializer(colleges, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(
                {"message": "not result found"}, status=status.HTTP_404_NOT_FOUND
            )


class LocationListView(APIView):
    def get(self, request):
        location = Location.objects.all()
        serializer = LocationDetailsSerializer(location, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LocationBasedCollegeListView(APIView):
    def get(self, request):

        location_id = request.data.get("id")
        print(location_id)
        college = College.objects.filter(location=location_id)
        serializer = CollegeDetailsSerializer(college, many=True)
        return Response(serializer.data)


class StudentProfileUpdateView(APIView):
    def put(self, request):
        permission_classes = [IsAuthenticatedWithJWT]

        data = request.data
        user = request.data.get("user")
        student = Student.objects.get(user=user)
        serializer = StudentProfileSerializer(student, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Student updated successfully", "profile": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollegeProfileUpdateView(APIView):
    def put(self, request):
        permission_classes = [IsAuthenticatedWithJWT]

        data = request.data
        user = request.data.get("user")
        college = College.objects.get(user=user)
        serializer = CollegeProfileSerializer(college, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "College updated successfully", "profile": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollegeDetailsView(APIView):
    def get(self, request, college_id):
        permission_classes = [IsAuthenticatedWithJWT]

        # college_id = request.data.get("id")
        college = College.objects.get(id=college_id)
        serializer = CollegeDetailsSerializer(college)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchView(APIView):
    def get(self, request):
        permission_classes = [IsAuthenticatedWithJWT]

        query = request.query_params.get("query", None)

        if not query:
            return Response(
                {"message": "Query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            course_results = []
            college_results = []

            if Course.objects.exists():
                course_q = Q(course_name__icontains=query)
                courses = Course.objects.filter(course_q)
                course_results = CourseDetailsSerializer(courses, many=True).data

            if College.objects.exists():
                college_q = (
                    Q(college_name__icontains=query)
                    | Q(location__location_name__icontains=query)
                    | Q(courses__course_name__icontains=query)
                )
                colleges = (
                    College.objects.filter(college_q)
                    .select_related("location")
                    .prefetch_related("courses")
                    .distinct()
                )
                college_results = CollegeDetailsSerializer(colleges, many=True).data

            result = {
                "courses": course_results,
                "colleges": college_results,
            }

            return Response(result, status=status.HTTP_200_OK)

        except ObjectDoesNotExist as e:
            return Response(
                {"message": "not found.", "details": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"message": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
