from django.urls import path, re_path
from .views import *

app_name = "cla_ca"
urlpatterns = [
    re_path("election/ca", ElectionVoteView.as_view(), name="vote"),
    path("ca/<int:election_pk>/box", ElectionVoteBoxView.as_view(), name="box")
]