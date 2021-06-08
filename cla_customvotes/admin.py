from django.contrib import admin
from django.shortcuts import resolve_url
from django.utils.html import mark_safe, escape
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from .models import *


@admin.register(Election)
class CampaignAdmin(admin.ModelAdmin):

    class CandidateInline(admin.StackedInline):
        fields = ['first_name', 'last_name', 'photo']
        model = Candidate
        extra = 0
        classes = ['collapse']

    class ProxiesInline(admin.StackedInline):
        autocomplete_fields = ['user']
        fields = ['user', 'names', 'total', 'voted_on']
        readonly_fields = ['total', 'voted_on']
        model = VoteProxy
        extra = 0
        classes = ['collapse']

        def total(self, obj: VoteProxy):
            return obj.total
        total.short_description = 'Nombre de voix'

    fields = ('name', ('starts_on', 'ends_on'), 'is_active', 'vote_link', 'vote_result', 'vote_votes')
    readonly_fields = ['vote_link', 'vote_result', 'vote_votes', 'election_school_year']
    list_display = ('election_label', 'election_school_year', 'election_start')
    ordering = "-starts_on",
    inlines = [
        CandidateInline,
        ProxiesInline
    ]

    def election_label(self, obj: Election):
        return obj.name
    election_label.short_description = 'Vote'

    def election_school_year(self, obj: Election):
        return f"{obj.school_year}/{obj.school_year+1}"
    election_school_year.short_description = 'Année scolaire'

    def election_start(self, obj: Election):
        return obj.starts_on.strftime('%d/%m/%Y')
    election_start.short_description = 'Début'

    def vote_link(self, obj: Election):
        if obj.pk:
            return mark_safe(f"<input class='vTextField' value='https://{escape(settings.ALLOWED_HOSTS[0]+resolve_url('cla_customvotes:vote', obj.uuid))}'>")
        else:
            return ""
    vote_link.short_description = 'Lien vers la page de vote'

    def vote_result(self, obj: Election):
        return mark_safe(
            render_to_string(
                "cla_customvotes/admin/vote_result.html",
                {
                    'election': obj
                }
            )
        )
    vote_result.short_description = "Résultat"

    def vote_votes(self, obj: Election):
        return mark_safe(
            render_to_string(
                "cla_customvotes/admin/votes.html",
                {
                    'election': obj
                }
            )
        )
    vote_votes.short_description = "Votants"
