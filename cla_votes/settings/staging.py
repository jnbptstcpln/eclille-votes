"""
Préproduction : mêmes réglages que la prod, mais aucun mail réel n'est envoyé
(ils s'affichent dans les logs du conteneur).
"""
import os

# base.py exige ces variables SMTP ; inutiles ici car le backend est surchargé plus bas.
os.environ.setdefault("EMAIL_HOST", "unused")
os.environ.setdefault("EMAIL_LOGIN", "unused")
os.environ.setdefault("EMAIL_PASSWORD", "unused")

from .coolify import *  # noqa: E402,F401,F403

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
