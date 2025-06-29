from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # admin
    path("admin/", admin.site.urls),
    # docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(), name="redoc"),
    # apps
    path("api/habits/", include("habits.urls", namespace="habits")),
    path("api/users/", include("users.urls", namespace="users")),
]
