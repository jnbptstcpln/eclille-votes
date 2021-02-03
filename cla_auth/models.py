from django.db import models
from django.contrib.auth.models import User


class UserInfos(models.Model):
    """
        The UserInfo model extends user by adding new properties
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="infos")
    promo = models.IntegerField()
