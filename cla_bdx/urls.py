from django.urls import path
from .views import *

app_name = "cla_bdx"
urlpatterns = [
    path("", CurrentCampaignView.as_view(), name="current"),  # Current campaigns
    path("election/<str:type>", CampaignVoteView.as_view(), name="vote"),
    path("<int:campaign_pk>/box", CampaignVoteBoxView.as_view(), name="box"),
    path("archives", LastCampaignView.as_view(), name="last"),  # All campaign list
]