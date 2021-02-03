from django.contrib import admin
from django.utils.html import mark_safe
from django.template.loader import render_to_string
from django.utils import timezone

from .models import *


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):

    class ListInline(admin.TabularInline):
        fields = ['name', 'logo', 'program']
        model = List

    class VoteInline(admin.TabularInline):
        fields = ['starts_on', 'ends_on', 'status', 'voters']
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

    fields = ('campaign_school_year', 'type', ('starts_on', 'ends_on'), 'vote_result')
    readonly_fields = ['vote_result', 'campaign_school_year']
    list_display = ('campaign_label', 'campaign_start', 'campaign_end', 'campaign_vote')
    inlines = [
        ListInline,
        VoteInline,
    ]

    def campaign_label(self, obj: Campaign):
        return f"{obj.get_type_display()} {obj.starts_on.year}"
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

    def vote_result(self, obj: Campaign):
        return mark_safe(
            render_to_string(
                "cla_bdx/admin/vote_result.html",
                {
                    'campaign': obj
                }
            )
        )
    vote_result.short_description = "Résultat des votes"
