from __future__ import annotations

from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import HasFunction

from .models import SettingDict, SettingValue
from .serializers import SettingDictSerializer, SettingValueSerializer


@extend_schema(
    tags=["settings"],
    description="CRUD словаря настроек.",
    responses={200: SettingDictSerializer},
)
class SettingDictViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = SettingDict.objects.all().order_by("id")
    serializer_class = SettingDictSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]


@extend_schema(
    tags=["settings"],
    description="CRUD значений настроек в разрезе компании (изоляция по company текущего пользователя).",
    responses={200: SettingValueSerializer},
)
class SettingValueViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SettingValueSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]

    def get_queryset(self):
        company = getattr(self.request.user, "company_id", None)
        return SettingValue.objects.select_related("setting").filter(company_id=company).order_by("-active_from")

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class EffectiveSettingView(APIView):
    """Вернуть эффективное значение настройки по коду: user > company (только активные по времени)."""

    permission_classes = [permissions.IsAuthenticated, HasFunction.required("settings:view")]

    @extend_schema(
        tags=["settings"],
        parameters=[OpenApiParameter(name="code", required=True, location=OpenApiParameter.PATH, type=str)],
        responses={
            200: OpenApiResponse(
                response=dict,
                description="Эффективное значение настройки",
                examples=[
                    OpenApiExample(
                        "company-scope",
                        value={"code": "theme", "scope": "company", "value": {"color": "light"}},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "user-scope",
                        value={"code": "theme", "scope": "user", "value": {"color": "dark"}},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "not-found",
                        value={"code": "unknown", "scope": None, "value": None},
                        response_only=True,
                    ),
                ],
            ),
            404: OpenApiResponse(description="Setting not found"),
        },
        description="Ищет активные (по времени) значения: сначала на уровне пользователя, затем на уровне компании.",
    )
    def get(self, request, code: str):
        now = timezone.now()
        try:
            sdict = SettingDict.objects.get(code=code)
        except SettingDict.DoesNotExist:
            return Response({"detail": "Setting not found."}, status=status.HTTP_404_NOT_FOUND)

        user_val = (
            (
                SettingValue.objects.filter(setting=sdict, user=request.user, active_from__lte=now).filter(
                    active_to__isnull=True
                )
                | SettingValue.objects.filter(setting=sdict, user=request.user, active_to__gte=now)
            )
            .order_by("-active_from")
            .first()
        )

        if user_val:
            return Response({"code": code, "scope": "user", "value": user_val.value})

        company_id = getattr(request.user, "company_id", None)
        comp_val = (
            (
                SettingValue.objects.filter(setting=sdict, company_id=company_id, active_from__lte=now).filter(
                    active_to__isnull=True
                )
                | SettingValue.objects.filter(setting=sdict, company_id=company_id, active_to__gte=now)
            )
            .order_by("-active_from")
            .first()
        )

        if comp_val:
            return Response({"code": code, "scope": "company", "value": comp_val.value})

        return Response({"code": code, "scope": None, "value": None}, status=status.HTTP_200_OK)
