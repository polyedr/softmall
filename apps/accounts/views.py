from __future__ import annotations

from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MeSerializer, RegisterCompanySerializer, RegisterUserSerializer


class RegisterCompanyView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["accounts"],
        request=RegisterCompanySerializer,
        responses={
            201: OpenApiResponse(
                response=dict,
                description="Company and initial admin user created",
                examples=[
                    OpenApiExample(
                        "Created",
                        value={"company_id": 1, "admin_id": 2},
                        response_only=True,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Payload",
                value={
                    "name": "Soft Corp",
                    "admin_username": "admin",
                    "admin_email": "admin@example.com",
                    "admin_password": "admin",
                },
                request_only=True,
            )
        ],
        description="Создаёт компанию, администратора, роль `admin` и базовые функции. Идемпотентно по (name, admin_username).",
    )
    @transaction.atomic
    def post(self, request):
        serializer = RegisterCompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)


class RegisterUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        request=RegisterUserSerializer,
        responses={201: OpenApiResponse(response=dict, description="User created")},
        description="Создаёт обычного пользователя в указанной компании.",
    )
    @transaction.atomic
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        responses={200: MeSerializer},
        description="Возвращает профиль текущего пользователя, его активные роли и функции.",
    )
    def get(self, request):
        return Response(MeSerializer(request.user).data)
