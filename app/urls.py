from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('create-post', login_required(views.PostCreate.as_view()), name="create_post"),
]
