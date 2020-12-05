from django.shortcuts import render
from django.views.generic import View


class AbstractPublicView(View):

    def context(self, context):
        context['active_navigation'] = ""
        return context


class IndexPublicView(AbstractPublicView):

    def get(self, req):
        return render(req, "cla_public/index.html")


class BoxElectionSvgView(View):
    def get(self, req):
        return render(
            req,
            "components/box_election.svg",
            {'election': "BDE 2021"},
            content_type="image/svg+xml"
        )