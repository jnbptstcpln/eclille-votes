from django.contrib import admin
from django.utils.html import escape

from .models import *


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):

    class ListInline(admin.TabularInline):
        fields = ['name', 'logo', 'program']
        model = List


    class VoteInline(admin.TabularInline):
        model = Vote
        extra = 0

    fields = ('type', ('starts_on', 'ends_on'))
    list_display = ('campaign_label', 'campaign_start', 'campaign_end', 'campaign_vote')
    inlines = [
        ListInline,
        VoteInline,
    ]

    def campaign_label(self, obj: Campaign):
        return f"{obj.get_type_display()} {obj.starts_on.year}"
    campaign_label.short_description = 'Campagne'

    def campaign_start(self, obj: Campaign):
        return obj.starts_on.strftime('%d/%m/%Y')
    campaign_start.short_description = 'Début'

    def campaign_end(self, obj: Campaign):
        return obj.ends_on.strftime('%d/%m/%Y')
    campaign_end.short_description = 'Fin'

    def campaign_vote(self, obj: Campaign):
        if obj.vote is None:
            return "Aucun vote planifié"
        return f"{obj.vote.starts_on.strftime('%d/%m/%Y')} : {obj.vote.starts_on.strftime('%Hh%i')} - {obj.vote.ends_on.strftime('%Hh%i')}"
    campaign_vote.short_description = 'Vote'
