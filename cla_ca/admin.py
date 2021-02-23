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
        fields = ['first_name', 'last_name', 'college', 'cover_letter', 'photo']
        model = Candidate

    fields = ('election_school_year', ('starts_on', 'ends_on'), 'vote_link', 'vote_result', 'vote_participation_stats')
    readonly_fields = ['vote_link', 'vote_result', 'vote_participation_stats', 'election_school_year']
    list_display = ('election_label', 'election_school_year', 'election_start')
    ordering = "-starts_on",
    inlines = [
        CandidateInline,
    ]

    def election_label(self, obj: Election):
        return f"Election CA {obj.starts_on.strftime('%m/%Y')}"
    election_label.short_description = 'Election CA'

    def election_school_year(self, obj: Election):
        return f"{obj.school_year}/{obj.school_year+1}"
    election_school_year.short_description = 'Année scolaire'

    def election_start(self, obj: Election):
        return obj.starts_on.strftime('%d/%m/%Y')
    election_start.short_description = 'Début'

    def vote_link(self, obj: Election):
        return mark_safe(f"<input class='vTextField' value='https://{escape(settings.ALLOWED_HOSTS[0]+resolve_url('cla_ca:vote'))}'>")
    vote_link.short_description = 'Lien vers la page de vote'

    def vote_result(self, obj: Election):
        return mark_safe(
            render_to_string(
                "cla_ca/admin/vote_result.html",
                {
                    'election': obj
                }
            )
        )
    vote_result.short_description = "Résultat"

    def vote_participation_stats(self, obj: Election):
        return mark_safe(
            render_to_string(
                "cla_ca/admin/vote_participation_stats.html",
                {
                    'election': obj
                }
            )
        )
    vote_participation_stats.short_description = "Participation"
