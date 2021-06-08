from django.urls import path, re_path
from .views import *

app_name = "cla_customvotes"
urlpatterns = [
    path("votes/<str:vote_uuid>", ElectionVoteView.as_view(), name="vote"),
    path("votes/<str:vote_uuid>/procurations", ElectionVoteProxyView.as_view(), name="vote_proxy")
]