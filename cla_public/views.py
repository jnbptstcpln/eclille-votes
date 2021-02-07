from django.shortcuts import render
from django.views.generic import View

from cla_bdx.models import Campaign


class AbstractPublicView(View):

    def context(self, context=dict()):
        context['active_navigation'] = context.get('active_navigation', "accueil")
        return context


class IndexPublicView(AbstractPublicView):

    def get(self, req):

        on_going_campaign_vote = Campaign.objects.vote_ongoing()

        return render(
            req,
            "cla_public/index.html",
            self.context({
                'on_going_campaign_vote': on_going_campaign_vote
            })
        )


class BoxElectionSvgView(View):
    def get(self, req):
        return render(
            req,
            "components/box_election.svg",
            {'election': "BDE 2021"},
            content_type="image/svg+xml"
        )