from django.contrib import admin
from django.shortcuts import resolve_url
from django.utils.html import mark_safe, escape
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from .models import *


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):

    class ListInline(admin.TabularInline):
        fields = ['name', 'logo', 'program', 'penality']
        model = List

    class VoteInline(admin.TabularInline):
        fields = ['starts_on', 'ends_on', 'status', 'voters', 'display_result_on']
        readonly_fields = ['status', 'voters']
        model = Vote
        extra = 0

        def voters(self, obj: Vote):
            return obj.votes.count()
        voters.short_description = 'Votants'

        def status(self, obj: Vote):
            if obj.starts_on is None or obj.ends_on is None:
                return "Mal défini"
            elif obj.starts_on > timezone.now():
                return "Planifié"
            elif obj.ends_on <= timezone.now():
                return "Terminé"
            else:
                return "En cours"
        status.short_description = "Statut"

    fields = ('campaign_school_year', 'type', ('starts_on', 'ends_on'), 'vote_link', 'vote_result', 'vote_participation_stats', 'vote_penalities')
    readonly_fields = ['vote_link', 'vote_result', 'vote_participation_stats', 'vote_penalities', 'campaign_school_year']
    list_display = ('campaign_label', 'campaign_start', 'campaign_end', 'campaign_vote')
    ordering = "-starts_on",
    inlines = [
        ListInline,
        VoteInline,
    ]

    def campaign_label(self, obj: Campaign):
        return f"{obj.school_year}/{obj.school_year+1} - {obj.get_type_display()}"
    campaign_label.short_description = 'Campagne'

    def campaign_school_year(self, obj: Campaign):
        return f"{obj.school_year}/{obj.school_year+1}"
    campaign_school_year.short_description = 'Année scolaire'

    def campaign_start(self, obj: Campaign):
        return obj.starts_on.strftime('%d/%m/%Y')
    campaign_start.short_description = 'Début'

    def campaign_end(self, obj: Campaign):
        return obj.ends_on.strftime('%d/%m/%Y')
    campaign_end.short_description = 'Fin'

    def campaign_vote(self, obj: Campaign):
        if obj.vote is None:
            return "Aucun vote planifié"
        return f"{obj.vote.starts_on.strftime('%d/%m/%Y')} : {obj.vote.starts_on.strftime('%Hh%M')} - {obj.vote.ends_on.strftime('%Hh%M')}"
    campaign_vote.short_description = 'Vote'

    def vote_link(self, obj: Campaign):
        if obj.vote:
            return mark_safe(f"<input class='vTextField' value='https://{escape(settings.ALLOWED_HOSTS[0]+resolve_url('cla_bdx:vote', type=obj.type))}'>")
        return "Aucun vote planifié"
    vote_link.short_description = 'Lien vers la page de vote'

    def vote_penalities(self, obj: Campaign):
        return mark_safe(
            render_to_string(
                "cla_bdx/admin/vote_penality.html",
                {
                    'campaign': obj
                }
            )
        )
    vote_penalities.short_description = "Pénalités"

    def vote_result(self, obj: Campaign):
        return mark_safe(
            render_to_string(
                "cla_bdx/admin/vote_result.html",
                {
                    'campaign': obj
                }
            )
        )
    vote_result.short_description = "Résultat"

    def vote_participation_stats(self, obj: Campaign):
        return mark_safe(
            render_to_string(
                "cla_bdx/admin/vote_participation_stats.html",
                {
                    'campaign': obj
                }
            )
        )
    vote_participation_stats.short_description = "Participation"


@admin.register(CampaignRegulation)
class CampaignRegulationAdmin(admin.ModelAdmin):
    ordering = "-voted_on",
