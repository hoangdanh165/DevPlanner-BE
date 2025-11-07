import os
from google.oauth2 import id_token
import requests
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db.models import Exists, OuterRef

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework import status
from rest_framework_simplejwt.tokens import BlacklistedToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.contrib.auth.hashers import make_password
from ..models import UserResetPassword
from django.utils import timezone
from ..serializers import UserSerializer, UserResetPasswordSerializer

from ..models import User, UserResetPassword
from ..serializers.user import StaffSerializer
from django.db.models.functions import TruncMonth, TruncDate
from django.utils.timezone import now
from django.db.models import Count, Q
from core.utils.response import success_response, error_response

from ..serializers.user import (
    UserInfoSerializer,
    UserAccountSerializer,
    UserProfileSerializer,
)
from ..tasks.email import run_send_password_reset_email, run_send_verification_email

from core.permissions import (
    IsAdmin,
)

CLIENT_ID = os.environ.get("CLIENT_ID")


class UserViewSet(viewsets.ModelViewSet):
    # queryset = User.objects.all().order_by('id')

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    # pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return UserSerializer
        elif self.action == "retrieve":
            return UserSerializer
        elif self.action == "create":
            return UserAccountSerializer
        elif self.action in ["update", "partial_update"]:
            return UserAccountSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def perform_update(self, serializer):
        if serializer.instance != self.request.user:
            return Response(
                {"error": "You can only update your own account!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance != self.request.user:
            return Response(
                {"error": "You can only delete your own account!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.delete()

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def partial_update_user(self, request, pk=None):
        try:
            user = self.get_object()
        except User.DoesNotExist:
            return Response(
                {"error": "User not found!"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserAccountSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["post"],
        url_path="create-user",
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def create_user(self, request, pk=None):
        data = request.data
        serializer = UserAccountSerializer(data=data)

        if "password" not in data or not data["password"]:
            data["password"] = "12345678"

        print(request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(
                    UserSerializer(user).data, status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": "Failed to create user."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def patch(self, request, pk, format=None):
    #     try:
    #         user = User.objects.get(pk=pk)
    #     except User.DoesNotExist:
    #         return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    #     serializer = UserAccountSerializer(user, data=request.data, partial=True)

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["put"],
        url_path="update-profile",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def update_profile(self, request):
        user = request.user

        user_data = {
            "phone": request.data.get("phone"),
            "full_name": request.data.get("fullName"),
            "address": request.data.get("address"),
            "email": request.data.get("email"),
        }

        if (
            "avatar" in request.data
            and isinstance(request.data["avatar"], str)
            and request.data["avatar"].startswith("http")
        ):
            user_data["avatar"] = user.avatar
        else:
            user_data["avatar"] = request.data.get("avatar")

        serializer = UserProfileSerializer(user, data=user_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["post"],
        url_path="sign-up",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def sign_up(self, request):
        data = request.data.copy()

        if "role" not in data or not data["role"]:
            data["role"] = {"name": "user"}

        serializer = UserAccountSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            run_send_verification_email.delay(user)

            return success_response(
                None,
                "Account created successfully, please check your email!",
                status=201,
            )

        return error_response("Validation failed", errors=serializer.errors)

    @action(
        methods=["post"],
        url_path="send-verification-email",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def send_verification_email(self, request):
        email = request.data.get("email")
        user = request.user

        if not email:
            return Response(
                {"status": "Please provide your email!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.email.strip().lower() != email.lower():
            return Response(
                {"status": "Email does not match your account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        run_send_verification_email.delay(user.id)

        return Response(
            {"status": "Verification email sent, please check your email!"},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["get"],
        url_path="verify-email",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def verify_email(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        user_id = verify_token(token)
        if user_id is None:
            return Response(
                {"status": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, id=user_id)
        if user.email_verified == True:
            return render(
                request,
                "user/email/email_verified.html",
                {"frontend_host": settings.FE_HOST},
            )

        user.email_verified = True
        user.save()

        return render(
            request,
            "user/email/email_verification_success.html",
            {"frontend_host": settings.FE_HOST},
        )

    @action(
        methods=["post"],
        url_path="forgot-password",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def forgot_password(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        run_send_password_reset_email.delay(user.id)
        return Response(
            {"status": "Password reset link has been sent to your email"},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["get"],
        url_path="handle-forgot-password",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def handle_forgot_password(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        user_id = verify_token(token)
        if user_id is None:
            return Response(
                {"error": "Invalid or expired token!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not UserResetPassword.objects.filter(user_id=user_id, token=token).exists():
            UserResetPassword.objects.create(
                user=User.objects.get(id=user_id),
                token=token,
                expired_time=timezone.now() + timezone.timedelta(hours=1),
            )

        if UserResetPassword.objects.filter(
            user_id=user_id, token=token, confirmed=True
        ).exists():
            return render(
                request,
                "user/reset_password/reset-password-expired.html",
                {"frontend_host": settings.FE_HOST},
            )

        return render(
            request,
            "user/reset_password/reset-password-form.html",
            {"token": token, "frontend_host": settings.FE_HOST},
        )

    @action(
        methods=["post"],
        url_path="reset-password",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def reset_password(self, request, *args, **kwargs):
        token = request.query_params.get("token")

        user_id = verify_token(token)

        user = User.objects.get(id=user_id)

        if not user:
            return Response(
                {"error": "No token provided!"}, status=status.HTTP_400_BAD_REQUEST
            )

        new_password = request.data.get("password")

        if not token or not new_password:
            return Response(
                {"error": "Token and new password are required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reset_entry = UserResetPassword.objects.filter(token=token).first()

            if not reset_entry:
                return Response(
                    {"error": "Not found!"}, status=status.HTTP_400_BAD_REQUEST
                )
            if reset_entry.expired_time < timezone.now():
                return Response(
                    {"error": "Token has expired!"}, status=status.HTTP_400_BAD_REQUEST
                )
            if reset_entry.confirmed == True:
                return Response({"error": "This link is expired!"})

            user = reset_entry.user

            user.password = make_password(new_password)
            user.save()
            reset_entry.confirmed = True
            reset_entry.save()
            return Response(
                {"message": "Password has been reset successfully!"},
                status=status.HTTP_200_OK,
            )

        except UserResetPassword.DoesNotExist:
            return Response(
                {"error": "Invalid token!"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=["post"],
        url_path="change-password",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def change_password(self, request, *args, **kwargs):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        user = request.user

        if not user.check_password(current_password):
            return Response(
                {"error": "Current password is not correct!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 8:
            return Response(
                {"error": "Password must have atleast 8 characters!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "Your password has been changed!"}, status=status.HTTP_200_OK
        )

    @action(
        methods=["get"],
        url_path="info",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def info(self, request):
        user = request.user
        serializer = UserInfoSerializer(user, context={"request": request})

        return Response(serializer.data)

    @action(
        methods=["get"],
        url_path="identity",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def identity(self, request):
        user = request.user
        serializer = UserSerializer(user)

        return Response(serializer.data)

    @action(
        methods=["post"],
        url_path="sign-out",
        detail=False,
        permission_classes=[IsAuthenticated],
        renderer_classes=[renderers.JSONRenderer],
    )
    def sign_out(self, request):
        try:
            refresh_token = request.COOKIES.get("refreshToken")

            token = RefreshToken(refresh_token)

            token.blacklist()
            response = Response(status=204)
            response.delete_cookie("refreshToken", path="/")

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(
        methods=["post"],
        url_path="sign-in",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def sign_in(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            check_user = User.objects.filter(email=email).first()

            if check_user:
                if not check_user.password:
                    return Response(
                        {
                            "error": "This account was registered using Google. Please sign in with Google."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            user = authenticate(request, username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                avatar = user.avatar
                full_name = user.full_name
                address = user.address

                if avatar:
                    avatar = avatar.url
                else:
                    avatar = None

                response = Response(
                    {
                        "userId": user.id,
                        "accessToken": access_token,
                        "refreshToken": refresh_token,
                        "role": user.role.name,
                        "status": user.status,
                        "avatar": avatar,
                        "fullName": full_name,
                        "phone": user.get_phone(),
                        "address": address,
                    },
                    status=status.HTTP_200_OK,
                )

                response.set_cookie(
                    key="refreshToken",
                    value=refresh_token,
                    httponly=True,
                    secure=True,  # True if Production mode is on
                    samesite="None",
                    max_age=24 * 60 * 60,
                )
                return response
            else:
                return Response(
                    {"error": "Invalid username or password!"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(
        methods=["post"],
        url_path="sign-in-with-google",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def sign_in_with_google(self, request):
        access_token = request.data.get("token")

        if not access_token:
            return Response({"error": "Missing access_token"}, status=400)

        google_user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"

        response = requests.get(
            google_user_info_url, headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            return Response({"error": "Invalid access token"}, status=400)

        user_info = response.json()

        email = user_info.get("email")
        email_verified = user_info.get("email_verified")
        full_name = user_info.get("name")
        avatar = user_info.get("picture")
        google_id = user_info.get("sub")

        user = User.objects.filter(google_id=google_id).first()

        if user:
            if user.email != email:
                user.email = email
                user.save()
        else:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": full_name,
                    "email_verified": email_verified,
                    "avatar_url": avatar,
                    "google_id": google_id,
                },
            )

            if not created:
                user.full_name = full_name
                user.avatar = avatar
                user.email_verified = email_verified
                user.google_id = google_id
                user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "userId": user.id,
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "role": user.role.name,
                "status": user.status,
                "avatar": avatar,
                "fullName": user.full_name,
                "email": user.email,
                "address": user.address,
                "phone": user.get_phone(),
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="refreshToken",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=24 * 60 * 60,
        )

        return response

    @action(
        methods=["post"],
        url_path="sign-in-with-github",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def sign_in_with_github(self, request):
        code = request.data.get("code")

        if not code:
            return Response({"error": "Missing authorization code"}, status=400)

        # ==============================
        # 1️⃣ Exchange code for access_token
        # ==============================
        token_url = "https://github.com/login/oauth/access_token"
        payload = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
        }
        headers = {"Accept": "application/json"}

        token_response = requests.post(token_url, json=payload, headers=headers)
        if token_response.status_code != 200:
            return Response({"error": "Failed to get access token"}, status=400)

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return Response({"error": "Invalid access token response"}, status=400)

        # ==============================
        # 2️⃣ Get GitHub user info
        # ==============================
        user_info_url = "https://api.github.com/user"
        email_info_url = "https://api.github.com/user/emails"

        user_info = requests.get(
            user_info_url, headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        email_info = requests.get(
            email_info_url, headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        # Lấy email chính xác (verified hoặc primary)
        primary_email = None
        if isinstance(email_info, list):
            for item in email_info:
                if item.get("primary") and item.get("verified"):
                    primary_email = item.get("email")
                    break

        # Lấy thông tin cơ bản
        github_id = user_info.get("id")
        username = user_info.get("login")
        avatar = user_info.get("avatar_url")
        name = user_info.get("name") or username
        email = primary_email or user_info.get("email")

        if not email:
            return Response({"error": "Email not available from GitHub"}, status=400)

        # # ==============================
        # # 5️⃣ Get user repositories
        # # ==============================
        # repos_url = "https://api.github.com/user/repos?per_page=50&sort=updated"
        # repos_response = requests.get(
        #     repos_url, headers={"Authorization": f"Bearer {access_token}"}
        # )

        # if repos_response.status_code == 200:
        #     repos_data = repos_response.json()
        # else:
        #     repos_data = []

        # # Chọn các trường cần thiết để lưu/gợi ý
        # user_repos = []
        # for repo in repos_data:
        #     user_repos.append(
        #         {
        #             "name": repo.get("name"),
        #             "description": repo.get("description"),
        #             "language": repo.get("language"),
        #             "topics": repo.get("topics", []),
        #             "stargazers_count": repo.get("stargazers_count"),
        #             "forks_count": repo.get("forks_count"),
        #             "html_url": repo.get("html_url"),
        #             "updated_at": repo.get("updated_at"),
        #         }
        #     )

        # print("User Repos:", user_repos)
        # TO-DO: Save user repos's information to database or suggest ideas based on these recent repos
        # ==============================
        # 3️⃣ Create or update user
        # ==============================
        user = User.objects.filter(github_id=github_id).first()

        if user:
            if user.email != email:
                user.email = email
                user.save()
        else:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": name,
                    "avatar_url": avatar,
                    "github_id": github_id,
                    "email_verified": True,
                },
            )
            if not created:
                user.github_id = github_id
                user.avatar_url = avatar
                user.full_name = name
                user.email_verified = True
                user.save()

        # ==============================
        # 4️⃣ Issue JWT tokens
        # ==============================
        refresh = RefreshToken.for_user(user)
        access_token_jwt = str(refresh.access_token)
        refresh_token_jwt = str(refresh)

        response = Response(
            {
                "userId": user.id,
                "accessToken": access_token_jwt,
                "refreshToken": refresh_token_jwt,
                "role": user.role.name if hasattr(user, "role") else None,
                "status": user.status if hasattr(user, "status") else None,
                "avatar": avatar,
                "fullName": user.full_name,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="refreshToken",
            value=refresh_token_jwt,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=24 * 60 * 60,
        )

        return response

    @action(
        methods=["post"],
        url_path="refresh",
        detail=False,
        permission_classes=[AllowAny],
        renderer_classes=[renderers.JSONRenderer],
    )
    def refresh(self, request):
        refresh_token = request.COOKIES.get("refreshToken")

        if not refresh_token:
            return Response(
                {"error": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)

            user_id = token["user_id"]
            user = User.objects.get(id=user_id)

            avatar = user.avatar

            if avatar:
                avatar = avatar.url
            elif user.avatar_url:
                avatar = user.avatar_url
            else:
                avatar = None

            return Response(
                {
                    "userId": user.id,
                    "accessToken": new_access_token,
                    "role": user.role.name,
                    "avatar": avatar,
                    "status": user.status,
                    "fullName": user.full_name,
                    "email": user.email,
                    "address": user.address,
                    "phone": user.get_phone(),
                },
                status=status.HTTP_200_OK,
            )

        except TokenError:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )

    @action(
        methods=["post"],
        detail=False,
        url_path="delete-multiple",
        permission_classes=[IsAdmin],
    )
    def delete_multiple(self, request):
        user_ids = request.data.get("ids", [])
        print(user_ids)
        if not user_ids:
            return Response(
                {"error": "No ID(s) found!"}, status=status.HTTP_400_BAD_REQUEST
            )

        users = User.objects.filter(id__in=user_ids)

        if not users.exists():
            return Response(
                {"error": "Can not found user(s) with provided ID(s)!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        deleted_count, _ = users.delete()

        return Response(
            {"message": f"Deleted {deleted_count} user(s) successfully!"},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["get"],
        url_path="get-all",
        detail=False,
        permission_classes=[IsAdmin],
        renderer_classes=[renderers.JSONRenderer],
    )
    def get_all(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
