from django.urls import path, re_path
from .views import *

app_name = "cla_bdx"
urlpatterns = [
    path("bdx", CurrentCampaignView.as_view(), name="current"),  # Current campaigns
    re_path("election/(?P<type>bd[a-z])", CampaignVoteView.as_view(), name="vote"),
    path("bdx/<int:campaign_pk>/box", CampaignVoteBoxView.as_view(), name="box"),
    path("bdx/<int:campaign_pk>/calendar", CampaignCalendarView.as_view(), name="calendar"),
    path("bdx/archives", LastCampaignView.as_view(), name="last"),  # All campaign list
]