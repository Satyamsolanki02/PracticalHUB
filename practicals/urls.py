
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("branch/<int:branch_id>/", views.branch_detail, name="branch_detail"),
]
