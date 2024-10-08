import random
from secrets import token_urlsafe

from django.contrib.auth.hashers import make_password
from rest_framework import status, permissions, generics, parsers, exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from articles.models import Article
from .errors import ACTIVE_USER_NOT_FOUND_ERROR_MSG

# from .models import Recommendation
from .models import Recommendation
from .serializers import UserSerializer, LoginSerializer, ValidationErrorSerializer, TokenResponseSerializer, \
    UserUpdateSerializer, ChangePasswordSerializer, ForgotPasswordRequestSerializer, ForgotPasswordResponseSerializer, \
    ForgotPasswordVerifyRequestSerializer, ForgotPasswordVerifyResponseSerializer, ResetPasswordResponseSerializer, \
    RecommendationSerializer

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from django_redis import get_redis_connection
from django.utils.translation import gettext_lazy as _
from .services import UserService, SendEmailService, OTPService

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary="Sign up a new User",
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: ValidationErrorSerializer
        }
    )
)
# SignUp qilish uchun class
class SignupView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'user': user_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        summary="Login a user",
        request=LoginSerializer,
        responses={
            200: TokenResponseSerializer,
            400: ValidationErrorSerializer
        }
    )
)
# Login qilish uchun class
class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': _('Hisob maʼlumotlari yaroqsiz')}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema_view(
    get=extend_schema(
        summary="Get user information",
        responses={
            200: UserSerializer,
            400: ValidationErrorSerializer
        }
    )
)
# User malumotlarni olish uchum class
class UsersMe(generics.RetrieveAPIView, generics.UpdateAPIView):
    http_method_names = ['get', 'patch']
    queryset = User.objects.filter(is_active=True)
    parser_classes = [parsers.MultiPartParser]
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer

    def patch(self, request, *args, **kwargs):
        redis_con = get_redis_connection('default')
        redis_con.set('test_key', 'test_value', ex=3600)
        cashed_value = redis_con.get('test_key')
        print(cashed_value)
        return super().partial_update(request, *args, **kwargs)


@extend_schema_view(
    post=extend_schema(
        summary="Log out a user",
        request=None,
        responses={
            200: ValidationErrorSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=None)
    def post(self, request, *args, **kwargs):
        UserService.create_tokens(request.user, access='fake_token', refresh='fake_token', is_force_add_to_redis=True)
        return Response({"detail": _("Muvafaqqiyatli chiqildi.")})


@extend_schema_view(
    put=extend_schema(
        summary="change user password",
        request=ChangePasswordSerializer,
        responses={
            200: TokenResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ChangePasswordSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=request.user.username,
            password=serializer.validated_data['old_password']
        )

        if user is not None:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            tokens = UserService.create_tokens(user, is_force_add_to_redis=True)
            return Response(tokens)
        else:
            raise ValidationError(_("Eski parol xato"))


@extend_schema_view(
    post=extend_schema(
        summary="Forgot Password",
        request=ForgotPasswordRequestSerializer,
        responses={
            200: ForgotPasswordResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ForgotPasswordView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordRequestSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        users = User.objects.filter(email=email, is_active=True)
        if not users.exists():
            raise exceptions.NotFound(ACTIVE_USER_NOT_FOUND_ERROR_MSG)

        otp_code, otp_secret = OTPService.generate_otp(email=email, expire_in=2 * 60)

        try:
            SendEmailService.send_email(email, otp_code)
            return Response({
                "email": email,
                "otp_secret": otp_secret,
            })
        except Exception:
            redis_conn = OTPService.get_redis_conn()
            redis_conn.delete(f"{email}:otp")
            raise ValidationError(_("Emailga xabar yuborishda xatolik yuz berdi"))


@extend_schema_view(
    post=extend_schema(
        summary="Forgot Password Verify",
        request=ForgotPasswordVerifyRequestSerializer,
        responses={
            200: ForgotPasswordVerifyResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ForgotPasswordVerifyView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordVerifyRequestSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        redis_conn = OTPService.get_redis_conn()
        otp_secret = kwargs.get('otp_secret')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data['otp_code']
        email = serializer.validated_data['email']
        users = User.objects.filter(email=email, is_active=True)
        if not users.exists():
            raise exceptions.NotFound(ACTIVE_USER_NOT_FOUND_ERROR_MSG)
        OTPService.check_otp(email, otp_code, otp_secret)
        redis_conn.delete(f"{email}:otp")
        token_hash = make_password(token_urlsafe())
        redis_conn.set(token_hash, email, ex=2 * 60 * 60)
        return Response({"token": token_hash})


@extend_schema_view(
    patch=extend_schema(
        summary="Reset Password",
        request=ResetPasswordResponseSerializer,
        responses={
            200: TokenResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ResetPasswordView(generics.UpdateAPIView):
    serializer_class = ResetPasswordResponseSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['patch']
    authentication_classes = []

    def patch(self, request, *args, **kwargs):
        redis_conn = OTPService.get_redis_conn()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_hash = serializer.validated_data['token']
        email = redis_conn.get(token_hash)

        if not email:
            raise ValidationError(_("Token yaroqsiz"))

        users = User.objects.filter(email=email.decode(), is_active=True)
        if not users.exists():
            raise exceptions.NotFound(ACTIVE_USER_NOT_FOUND_ERROR_MSG)

        password = serializer.validated_data['password']
        user = users.first()
        user.set_password(password)
        user.save()

        update_session_auth_hash(request, user)
        tokens = UserService.create_tokens(user, is_force_add_to_redis=True)
        redis_conn.delete(token_hash)
        return Response(tokens)


@extend_schema_view(
    patch=extend_schema(
        summary="Recommend View",
        request=RecommendationSerializer,
        responses={
            204: RecommendationSerializer,
            404: RecommendationSerializer
        }
    )
)
class RecommendationView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecommendationSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        more_article_id = request.data.get('more_article_id')
        less_article_id = request.data.get('less_article_id')
        recommendation, created = Recommendation.objects.get_or_create(user=user)

        if more_article_id:
            article = Article.objects.get(id=more_article_id)
            recommendation.add_to_more_recommend(article)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if less_article_id:
            article = Article.objects.get(id=less_article_id)
            recommendation.add_to_less_recommend(article)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
