from django.shortcuts import render
from django.views.generic import View


class AbstractPublicView(View):

    def context(self, context):
        context['active_navigation'] = ""
        return context


class IndexPublicView(AbstractPublicView):

    def get(self, req):
        return render(req, "cla_public")
