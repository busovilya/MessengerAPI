from django.contrib.auth.admin import User
from rest_framework import viewsets, status, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import UserSerializer
from rest_framework_jwt import authentication


class UserListView(viewsets.ModelViewSet):
    authentication_classes = (authentication.JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated, )
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterUserView(views.APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        email = request.data.get("email", "")
        if not username or not password:
            return Response(
                data={
                    "message": "username and password is required to register a user"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                data={
                    "message": "this username has been already registered"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        User.objects.create_user(
            username=username, password=password, email=email
        )
        return Response(status=status.HTTP_201_CREATED)