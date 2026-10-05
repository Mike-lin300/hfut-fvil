from django.urls import path

from .views import doclib_home

urlpatterns = [
    path("", doclib_home, name="doclib_home"),
]
