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

    def get(self, req):
        election = Election.objects.ongoing()
        if election is None:
            raise Http404()

        if election.did_user_vote(req.user):
            return self.render_already_vote(election)

        college = election.get_computed_user_college()
        form = CaVoteForm(candidates=election.candidates.filter(college=college))

        return render(
            req,
            "cla_ca/member/vote.html",
            self.context({
                'election': election,
                'form': form
            })
        )

    def post(self, req):
        election = Election.objects.ongoing()
        if election is None:
            raise Http404()

        if election.did_user_vote(req.user):
            return self.render_already_vote(election)

        college = election.get_computed_user_college()
        form = CaVoteForm(req.POST, candidates=election.candidates.filter(college=college))

        if form.is_valid():

            candidate1_index = int(form.cleaned_data['vote1'])
            candidate2_index = int(form.cleaned_data['vote2'])

            if candidate1_index == 0 or candidate1_index != candidate2_index:

                # Register user vote
                election.register_user(req.user, college)

                if candidate1_index > 0:
                    try:
                        candidate1 = election.candidates.get(pk=candidate1_index)
                    except Candidate.DoesNotExist:
                        messages.error(req, "Votre vote n'a été validé, veuillez réessayer.")
                        return redirect("cla_ca:vote")

                    candidate1.votes = candidate1.votes + 1
                    candidate1.save()

                if candidate2_index > 0:
                    try:
                        candidate2 = election.candidates.get(pk=candidate2_index)
                    except Candidate.DoesNotExist:
                        messages.error(req, "Votre vote n'a été validé, veuillez réessayer.")
                        return redirect("cla_ca:vote")

                    candidate2.votes = candidate2.votes + 1
                    candidate2.save()

                return render(
                    req,
                    "cla_ca/member/did_vote.html",
                    self.context({'election': election})
                )

            else:
                form.add_error('vote2', "Vous ne pouvez pas donner vos deux votes au même candidat.")

        return render(
            req,
            "cla_ca/member/vote.html",
            self.context({
                'election': election,
                'form': form,
                'scroll': True
            })
        )

    def render_already_vote(self, election):
        return render(
            self.request,
            "cla_ca/member/already_vote.html",
            self.context({
                'election': election
            })
        )


class ElectionVoteBoxView(AbstractCaView):
    def get(self, req, election_pk):
        campaign = get_object_or_404(Election, pk=election_pk)
        return render(
            req,
            "components/box_election.svg",
            {'election': f"CA {campaign.starts_on.year}"},
            content_type="image/svg+xml"
        )