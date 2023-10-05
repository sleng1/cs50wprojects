from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.wiki, name="wiki"),
    path("new", views.create, name="new"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("random", views.choose_random, name="random"),
]