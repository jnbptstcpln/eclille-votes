from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http.response import Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone

from .models import *
from .forms import *


class AbstractCaView(View):

    def context(self, context=dict()):
        context['active_navigation'] = context.get('active_navigation', "ca")
        return context


@method_decorator(login_required, 'dispatch')
class ElectionVoteView(AbstractCaView):

    def get(self, req, vote_uuid):
        election = get_object_or_404(Election, uuid=vote_uuid)

        if not election.should_access_vote():
            return render(
                req,
                "cla_customvotes/member/vote_closed.html",
                self.context({
                    'election': election
                })
            )

        if election.did_user_vote(req.user):
            return self.render_already_vote(election)

        form = CustomVoteForm(candidates=election.candidates.all())

        return render(
            req,
            "cla_customvotes/member/vote.html",
            self.context({
                'election': election,
                'form': form
            })
        )

    def post(self, req, vote_uuid):
        election = get_object_or_404(Election, uuid=vote_uuid)

        if not election.should_access_vote():
            return render(
                req,
                "cla_customvotes/member/vote_closed.html",
                self.context({
                    'election': election
                })
            )

        if election.did_user_vote(req.user):
            return self.render_already_vote(election)

        form = CustomVoteForm(req.POST, candidates=election.candidates.all())

        if form.is_valid():

            candidate1_index = int(form.cleaned_data['vote1'])

            # Register user vote
            election.register_user(req.user)

            if candidate1_index > 0:
                try:
                    candidate1 = election.candidates.get(pk=candidate1_index)
                except Candidate.DoesNotExist:
                    messages.error(req, "Votre vote n'a été validé, veuillez réessayer.")
                    return redirect("cla_ca:vote")

                candidate1.votes = candidate1.votes + 1
                candidate1.save()

            return render(
                req,
                "cla_customvotes/member/did_vote.html",
                self.context({
                    'election': election,
                    'proxy': election.proxies.filter(user=req.user, voted_on__isnull=True).first()
                })
            )

        return render(
            req,
            "cla_customvotes/member/vote.html",
            self.context({
                'election': election,
                'form': form,
                'scroll': True
            })
        )

    def render_already_vote(self, election):
        return render(
            self.request,
            "cla_customvotes/member/already_vote.html",
            self.context({
                'election': election,
                'proxy': election.proxies.filter(user=self.request.user, voted_on__isnull=True).first()
            })
        )


@method_decorator(login_required, 'dispatch')
class ElectionVoteProxyView(AbstractCaView):

    def get(self, req, vote_uuid):
        election = get_object_or_404(Election, uuid=vote_uuid)

        if not election.should_access_vote():
            return render(
                req,
                "cla_customvotes/member/vote_closed.html",
                self.context({
                    'election': election
                })
            )

        if not election.has_user_proxy(req.user):
            return render(
                req,
                "cla_customvotes/member/vote_noproxy.html",
                self.context({
                    'election': election
                })
            )

        if election.did_user_proxy_vote(req.user):
            return self.render_already_vote(election)

        form = CustomVoteProxyForm(proxy=election.get_user_proxy(req.user), candidates=election.candidates.all())

        print(election.get_user_proxy(req.user))

        return render(
            req,
            "cla_customvotes/member/vote_proxy.html",
            self.context({
                'election': election,
                'form': form,
                'proxy': election.get_user_proxy(req.user)
            })
        )

    def post(self, req, vote_uuid):
        election = get_object_or_404(Election, uuid=vote_uuid)

        if not election.should_access_vote():
            return render(
                req,
                "cla_customvotes/member/vote_closed.html",
                self.context({
                    'election': election
                })
            )

        if not election.has_user_proxy(req.user):
            return render(
                req,
                "cla_customvotes/member/vote_noproxy.html",
                self.context({
                    'election': election
                })
            )

        if election.did_user_proxy_vote(req.user):
            return self.render_already_vote(election)

        form = CustomVoteProxyForm(req.POST, proxy=election.get_user_proxy(req.user), candidates=election.candidates.all())

        if form.is_valid():
            # First save the vote
            proxy: VoteProxy = form.proxy
            proxy.voted_on = timezone.now()
            proxy.save()

            # Then update candidates urns
            for candidate in election.candidates.all():
                candidate.votes += form.get_vote_for(candidate)
                candidate.save()

            return render(
                req,
                "cla_customvotes/member/did_vote.html",
                self.context({
                    'election': election
                })
            )

        return render(
            req,
            "cla_customvotes/member/vote_proxy.html",
            self.context({
                'election': election,
                'form': form,
                'scroll': True,
                'proxy': election.get_user_proxy(req.user)
            })
        )

    def render_already_vote(self, election):
        return render(
            self.request,
            "cla_customvotes/member/already_vote.html",
            self.context({
                'election': election,
                'proxy': election.proxies.filter(user=self.request.user, voted_on__isnull=True).first()
            })
        )
