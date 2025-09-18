from __future__ import annotations

import hashlib

from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.models import IdempotencyKey

from .serializers import MeSerializer, RegisterCompanySerializer, RegisterUserSerializer


class RegisterCompanyView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["accounts"],
        request=RegisterCompanySerializer,
        parameters=[
            OpenApiParameter(
                name="Idempotency-Key",
                type=str,
                location=OpenApiParameter.HEADER,
                description="Ключ для идемпотентного запроса. "
                "Повторный POST с тем же key и body вернёт сохранённый ответ.",
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=dict,
                description="Компания и администратор успешно созданы",
                examples=[
                    OpenApiExample(
                        "Успешное создание",
                        value={"company_id": 1, "admin_id": 2},
                        response_only=True,
                    )
                ],
            ),
            200: OpenApiResponse(
                response=dict,
                description="Повторный запрос с тем же Idempotency-Key и телом. " "Возвращён сохранённый результат.",
            ),
            409: OpenApiResponse(description="Конфликт: Idempotency-Key совпадает, но тело запроса отличается."),
        },
        description=(
            "Создаёт компанию, администратора, роль `admin` и базовые функции.\n\n"
            "Если заголовок `Idempotency-Key` передан:\n"
            " первый вызов сохранит результат,\n"
            " повторный вызов с тем же key и идентичным body вернёт тот же ответ (200),\n"
            " если body отличается — будет 409 Conflict."
        ),
    )
    @transaction.atomic
    def post(self, request):
        idem_key = request.headers.get("Idempotency-Key")
        body_bytes = request.body or b""
        request_hash = hashlib.sha256(body_bytes).hexdigest()
        endpoint = request.path

        if idem_key:
            rec = IdempotencyKey.objects.filter(key=idem_key).first()
            if rec:
                if rec.endpoint != endpoint or rec.request_hash != request_hash:
                    return Response(
                        {"detail": "Idempotency-Key conflict."},
                        status=status.HTTP_409_CONFLICT,
                    )
                return Response(rec.response_json, status=rec.status_code)

        serializer = RegisterCompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        resp = Response(data, status=status.HTTP_201_CREATED)

        if idem_key:
            IdempotencyKey.objects.create(
                key=idem_key,
                endpoint=endpoint,
                request_hash=request_hash,
                user=getattr(request, "user", None) if getattr(request, "user", None).is_authenticated else None,
                status_code=resp.status_code,
                response_json=resp.data,
            )
        return resp


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
