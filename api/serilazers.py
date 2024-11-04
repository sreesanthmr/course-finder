from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserSerializer(serializers.Serializer):
    # class Meta:
    #     model = CustomUser
    #     fields = ["email", "password"]

    email = serializers.EmailField()
    password = serializers.CharField()
    name = serializers.CharField()

class StudentSerializer(serializers.Serializer):

    student_name = serializers.CharField()
    gender = serializers.CharField()
    location = serializers.CharField()



    # email = serializers.EmailField(write_only=True)
    # password = serializers.CharField(write_only=True)

    # class Meta:
    #     model = Student
    #     fields = ["email", "password", "name", "gender", "location"]

    # def create(self, validated_data):
    #     # Extract CustomUser fields
    #     email = validated_data.pop("email")
    #     password = validated_data.pop("password")
        
    #     # Create CustomUser instance first
    #     user = CustomUser.objects.create_user(email=email, password=password)
        
    #     # Now create Student instance and link with CustomUser
    #     student = Student.objects.create(customuser_ptr=user, **validated_data)
    #     return student




    # class Meta:
    #     model = Student
    #     fields = ["name", "gender", "location"]

    # def create(self, validated_data):
    #     # Extract fields specific to CustomUser
    #     email = validated_data.pop("email")
    #     password = validated_data.pop("password")
        
    #     # Create the Student instance (inherits from CustomUser)
    #     student = Student.objects.create_user(email=email, password=password, **validated_data)
        
    #     return student


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        exclude = ["created_at", "updated_at", "is_active", "is_superuser", "is_admin", "is_staff"]

    def create(self, validated_data):
        college = College.objects.create_user(**validated_data)
        college.is_active = True 
        college.save()
        return college


class AdminRegSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    name = serializers.CharField()

    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")
        name = validated_data.get("name")
        admin = CustomUser.objects.create_superuser(
            email=email,
            password=password,
            name=name,
        )
        return admin


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

        data["user"] = user
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
