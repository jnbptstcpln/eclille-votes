import random
import string

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.core.mail import send_mail
from django.http.response import Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone

from .models import *
from .forms import *


class AbstractEnsclView(View):

    def context(self, context=dict()):
        context['active_navigation'] = context.get('active_navigation', "enscl")
        return context


class EnsclLoginView(AbstractEnsclView):

    def get(self, req):
        login_form = EnsclLoginForm()
        return render(
            req,
            "cla_enscl/login/login.html",
            self.context({
                'form': login_form
            })
        )

    def post(self, req):
        login_form = EnsclLoginForm(req.POST)

        if login_form.is_valid():
            users = User.objects.filter(email=login_form.cleaned_data['email'])

            if users.count() > 0:
                user = users.first()
                user.code = '-'.join(
                    [''.join(random.choice(string.ascii_lowercase + string.digits) for j in range(4)) for i in range(2)]
                ).upper()
                send_mail(
                    "Code d'accès au vote",
                    f"Voici le code pour accéder au vote : {user.code}",
                    'cla@centralelille.fr',
                    [user.email],
                    fail_silently=True
                )
                user.email_sent_on = timezone.now()
                user.save()

                req.session['enscl_email'] = user.email
                return redirect("cla_enscl:code")
            else:
                login_form.add_error("email", "Cette adresse mail ne correspond à aucun compte")

        return render(
            req,
            "cla_enscl/login/login.html",
            self.context({
                'form': login_form
            })
        )


class EnsclCodeView(AbstractEnsclView):

    def get(self, req):

        email = req.session.get('enscl_email')
        if not email or User.objects.filter(email=email).count() == 0:
            return redirect("cla_enscl:login")

        user = User.objects.filter(email=email).first()

        code_form = EnsclCodeForm()
        return render(
            req,
            "cla_enscl/login/code.html",
            self.context({
                'form': code_form,
                'user': user
            })
        )

    def post(self, req):

        email = req.session.get('enscl_email')
        if not email or User.objects.filter(email=email).count() == 0:
            return redirect("cla_enscl:login")

        user = User.objects.filter(email=email).first()

        code_form = EnsclCodeForm(req.POST)

        if code_form.is_valid():
            if code_form.cleaned_data['code'] == user.code:
                req.session['enscl_user'] = user.email
                return redirect("cla_enscl:vote")

            else:
                code_form.add_error("code", "Le code que vous avez indiqué est incorrect.")

        return render(
            req,
            "cla_enscl/login/code.html",
            self.context({
                'form': code_form,
                'user': user
            })
        )


class EnsclVoteView(AbstractEnsclView):

    def get(self, req):

        email = req.session.get('enscl_user')
        if not email or User.objects.filter(email=email).count() == 0:
            return redirect("cla_enscl:login")

        user = User.objects.filter(email=email).first()

        election = Election.objects.ongoing()
        if election is None:
            raise Http404()

        if election.did_user_vote(user):
            return self.render_already_vote(election)

        form = EnsclVoteForm()

        return render(
            req,
            "cla_enscl/member/vote.html",
            self.context({
                'election': election,
                'form': form
            })
        )

    def post(self, req):

        email = req.session.get('enscl_user')
        if not email or User.objects.filter(email=email).count() == 0:
            return redirect("cla_enscl:login")

        user = User.objects.filter(email=email).first()

        election = Election.objects.ongoing()
        if election is None:
            raise Http404()

        if election.did_user_vote(user):
            return self.render_already_vote(election)

        form = EnsclVoteForm(req.POST)

        if form.is_valid():
            UserVote.objects.create(
                user=user,
                election=election,
                content=form.cleaned_data
            )
            return render(
                req,
                "cla_enscl/member/did_vote.html",
                self.context({
                    'election': election
                })
            )

        return render(
            req,
            "cla_enscl/member/vote.html",
            self.context({
                'election': election,
                'form': form
            })
        )

    def render_already_vote(self, election):
        return render(
            self.request,
            "cla_enscl/member/already_vote.html",
            self.context({
                'election': election
            })
        )