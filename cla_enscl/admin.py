from django.contrib import admin
from django.shortcuts import resolve_url
from django.utils.html import mark_safe, escape
from django.template.loader import render_to_string
from django.conf import settings

from .models import *

admin.site.register(User)


@admin.register(Election)
class CampaignAdmin(admin.ModelAdmin):

    fields = (('starts_on', 'ends_on'), 'vote_link', 'vote_result')
    readonly_fields = ['vote_link', 'vote_result']

    def vote_link(self, obj: Election):
        return mark_safe(f"<input class='vTextField' value='https://{escape(settings.ALLOWED_HOSTS[0]+resolve_url('cla_enscl:vote'))}'>")
    vote_link.short_description = 'Lien vers la page de vote'

    def vote_result(self, obj: Election):
        return mark_safe(
            render_to_string(
                "cla_enscl/admin/vote_result.html",
                {
                    'election': obj
                }
            )
        )
    vote_result.short_description = "Résultat"
