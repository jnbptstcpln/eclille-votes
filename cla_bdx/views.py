import datetime
import collections

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http.response import Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from cla_votes.utils import current_school_year
from cla_bdx.models import Campaign, List, CampaignRegulation
from cla_bdx.forms import BdxVoteForm


class AbstractBdxView(View):
    def context(self, context=dict()):
        context["active_navigation"] = context.get("active_navigation", "bdx")
        return context


class CurrentCampaignView(AbstractBdxView):
    def get(self, req):
        campaign_regulation = (
            CampaignRegulation.objects.filter(
                voted_on__gt=datetime.datetime(
                    year=current_school_year(), month=9, day=1
                )
            )
            .order_by("voted_on")
            .first()
        )
        current_campaigns = Campaign.objects.filter(
            starts_on__gt=datetime.datetime(year=current_school_year(), month=9, day=1)
        ).order_by("starts_on")
        on_going_campaigns = Campaign.objects.filter(
            starts_on__lt=timezone.now(), ends_on__gt=timezone.now()
        )
        return render(
            req,
            "cla_bdx/public/current.html",
            self.context(
                {
                    "campaign_regulation": campaign_regulation,
                    "campaigns": current_campaigns,
                    "on_going_campaigns": on_going_campaigns,
                }
            ),
        )


class CampaignCalendarView(AbstractBdxView):
    def get(self, req, campaign_pk):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)

        return render(
            req,
            "cla_bdx/public/calendar.ics",
            self.context({"campaign": campaign, "date_now": timezone.now()}),
            content_type="text/calendar",
        )


class LastCampaignView(AbstractBdxView):
    def get(self, req):
        campaigns = Campaign.objects.filter(
            starts_on__lt=datetime.datetime(year=current_school_year(), month=9, day=1)
        ).order_by("starts_on")

        campaigns_year = {}
        for campaign in campaigns:
            if campaigns_year.get(campaign.school_year, None) is None:
                campaigns_year[campaign.school_year] = []
            campaigns_year[campaign.school_year].append(campaign)

        campaigns_year_sorted = collections.OrderedDict(
            sorted(campaigns_year.items(), reverse=True)
        )

        return render(
            req,
            "cla_bdx/public/last.html",
            self.context(
                {
                    "active_navigation": "archives",
                    "campaigns_year": campaigns_year_sorted,
                }
            ),
        )


@method_decorator(login_required, "dispatch")
class CampaignVoteView(AbstractBdxView):
    def get(self, req, type):
        campaign = Campaign.objects.vote_ongoing(type)
        if campaign is None:
            raise Http404()

        if not campaign.should_display_vote():
            raise Http404()

        if not campaign.can_user_vote(req.user):
            return self.render_vote_access_refused(campaign)

        if campaign.did_user_vote(req.user):
            return self.render_already_vote(campaign)

        form = BdxVoteForm(campaign=campaign)

        return render(
            req,
            "cla_bdx/member/vote.html",
            self.context({"campaign": campaign, "form": form}),
        )

    def post(self, req, type):
        campaign = Campaign.objects.vote_ongoing(type)
        if campaign is None:
            raise Http404()

        if not campaign.should_display_vote():
            raise Http404()

        if not campaign.can_user_vote(req.user):
            return self.render_vote_access_refused(campaign)

        if campaign.did_user_vote(req.user):
            return self.render_already_vote(campaign)

        form = BdxVoteForm(req.POST, campaign=campaign)

        if form.is_valid():
            # Register user vote
            campaign.vote.register_user(req.user)

            list_index = int(form.cleaned_data["vote"])
            if list_index > 0:
                try:
                    list = campaign.lists.get(pk=list_index)
                except List.DoesNotExist:
                    messages.error(
                        req, "Votre vote n'a été validé, veuillez réessayer."
                    )
                    return redirect("cla_bdx:vote", type=campaign.type)

                list.votes_binary = list.votes_binary + 1
                list.save()

            return render(
                req,
                "cla_bdx/member/did_vote.html",
                self.context({"campaign": campaign}),
            )

        return render(
            req,
            "cla_bdx/member/vote.html",
            self.context({"campaign": campaign, "form": form}),
        )

    def render_vote_access_refused(self, campaign):
        return render(
            self.request,
            "cla_bdx/member/access_refused.html",
            self.context({"campaign": campaign}),
        )

    def render_already_vote(self, campaign):
        return render(
            self.request,
            "cla_bdx/member/already_vote.html",
            self.context({"campaign": campaign}),
        )


class CampaignVoteBoxView(AbstractBdxView):
    def get(self, req, campaign_pk):
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        campaign_type_display = campaign.type.upper()
        if campaign_type_display == "BDE_ENSCL":
            campaign_type_display = "ENSCL"
        return render(
            req,
            "components/box_election.svg",
            {"election": f"{campaign_type_display} {campaign.starts_on.year}"},
            content_type="image/svg+xml",
        )
