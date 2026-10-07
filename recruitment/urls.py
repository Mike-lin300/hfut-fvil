from django.urls import path

from . import views

urlpatterns = [
    path("", views.recruit_home, name="recruit_home"),
    path("signup/", views.signup, name="recruit_signup"),
    path("query/", views.query, name="recruit_query"),
    path("export/", views.export, name="recruit_export"),
    path("privacy/", views.privacy, name="recruit_privacy"),
]
