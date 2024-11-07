from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "password"]


class StudentRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["student_name", "gender", "location"]


class CollegeRegSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), many=True
    )

    class Meta:
        model = College
        fields = ["college_name", "location", "courses"]


class AdminRegSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["location_name"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["course_name"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        try:

            if user.is_student:
                student = Student.objects.get(user = user)
                user_data = {
                    "name": student.student_name,
                    "gender": student.gender,
                    "location": student.location.location_name,
                }
            
            elif user.is_college:
                college = College.objects.get(user=user)
                courses = CourseSerializer(college.courses.all(), many=True).data
                user_data = {
                    "college_name": college.college_name,
                    "courses": courses,
                    "location": college.location.location_name,
                }
            
        except Student.DoesNotExist:
            user_data = None    

        data["user"] = user
        data["user_data"] = user_data
        return data

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "message": "Login successful",
            "token": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }


class OtpVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")
        if not email or not otp:
            raise serializers.ValidationError("Both email and OTP are required.")
        return data
    

class CollegeListSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)  
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = College
        fields = ["college_name", "location", "courses"]
