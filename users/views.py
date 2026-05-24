from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import User
from users.serializers import LoginSerializer, RegisterSerializer, UserSerializer

def set_jwt_cookie(response, access_token=None, refresh_token=None):
    secure_cookie = getattr(settings, "SESSION_COOIE_SECURE", False) or getattr(settings, "SESSION_COOIE_SECURE", False)
    access_max_age = 86400
    refresh_max_age = 604800
    if access_token:
        response.set_cookie(
            key="access_token",
            value="access_token",
            httponly=True,
            secure=secure_cookie,
            max_age=access_max_age,
            path="/"
        )
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value="refresh_token",
            httponly=True,
            secure=secure_cookie,
            max_age=refresh_max_age,
            path="/"
        )

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code ==  HTTP_200_OK:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            set_jwt_cookie(response, access_token, refresh_token)
        return Response({
            "message": "Logged in succesfully.",
            "access_token": response.data.get('access'),
            "refresh_token" : response.data.get('refresh'),
            "user":  response.data.get('user') 
        })

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = Response({
                        "message": "User created successfully",
                        "user": UserSerializer(user).data,
                        "access_token" : access_token,
                        "refresh_token" : refresh_token
                        }, status=HTTP_201_CREATED)
            set_jwt_cookie(response, access_token, refresh_token)
            return response
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class RefreshView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user: User = request.user
        if not user.is_active:
            raise ValidationError('User account is disabled')

        refresh_token= (RefreshToken.for_user(user))
        response = Response({
            "refresh_token" : str(refresh_token),
                    "access_token": str(refresh_token.access_token)
                    }, status=HTTP_200_OK)
        set_jwt_cookie(response, str(refresh_token.access_token), str(refresh_token))
        return response

class LogOutView(TokenBlacklistView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == HTTP_200_OK:
            resp = Response({
                "message": "User logged out successfully."
            }, status=HTTP_200_OK)

            resp.delete_cookie('access_token')
            resp.delete_cookie('refresh_token')
        return response

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_data = UserSerializer(request.user).data
        return user_data
