import re

from django.db import models
from django.contrib.auth.models import User


class UserInfos(models.Model):
    """
        The UserInfo model extends user by adding new properties
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="infos")
    cursus = models.CharField(max_length=100, null=True)
    promo = models.IntegerField()

    def is_from_centrale(self):
        return re.match(r'^G\d.*', self.cursus)

    def is_from_iteem(self):
        return re.match(r'^IE\d.*', self.cursus)
