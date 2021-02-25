from django.urls import path, re_path
from .views import *

app_name = "cla_enscl"
urlpatterns = [
    path("", EnsclLoginView.as_view(), name="login"),
    path("code", EnsclCodeView.as_view(), name="code"),
    path("vote", EnsclVoteView.as_view(), name="vote"),
    #path("ca/<int:election_pk>/box", ElectionVoteBoxView.as_view(), name="box")
]