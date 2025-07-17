from django.urls import path
from api.users.views import CheckUserView


urlpatterns = [
    path("check/", CheckUserView.as_view(), name="check_user"),
]
