from django.conf import settings
from django.utils import timezone


def cla_votes_context(request):
    context = {}

    # Project version
    context['project_version'] = settings.PROJECT_VERSION

    # School year
    now = timezone.now()
    context['school_year'] = now.year - 1 if 1 <= now.month < 9 else now.year

    return context
