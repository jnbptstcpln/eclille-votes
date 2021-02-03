from django.shortcuts import render
from django.views.generic import View


class AbstractBdxView(View):

    def context(self, context):
        context['active_navigation'] = ""
        return context


class IndexPublicView(AbstractBdxView):

    def get(self, req):
        return render(req, "cla_public/index.html")
