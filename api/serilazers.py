from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "name",
            "email",
            "password",
            "gender",
            "location",
            "plustwo_percentage",
        ]


class CollegeRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        exclude = [
            "created_at",
            "updated_at",
        ]


class AdminRegSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    name = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):

        user = CustomUser.objects.filter(email=data["email"])
        if not user.exists():
            raise serializers.ValidationError("account not found")
        return data

    def get_jwt_token(self, data):
        # Authenticate the user using email and password
        user = authenticate(email=data["email"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        # Check if the user's account is active
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        # Generate the refresh and access tokens using Simple JWT

        refresh = RefreshToken.for_user(user)
        return {
            "message": "Login successful",
            "data": {
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            },
        }


class OtpVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")

        if not otp and not email:
            raise serializers.ValidationError("must include otp and username")
        return data
