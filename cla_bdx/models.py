import os
import uuid

from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth.models import User
from django.utils.text import slugify


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s-%s.%s" % (slugify(instance.name), uuid.uuid4(), ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def program(cls, instance, filename):
        return cls._path(instance, ["cla_bdx", "program"], filename)

    @classmethod
    def logo(cls, instance, filename):
        return cls._path(instance, ["cla_bdx", "logo"], filename)


class Campaign(models.Model):

    class Meta:
        ordering = '-starts_on',
        verbose_name = "Campagne"

    class BDX(models.TextChoices):
        BDA = 'bda', 'BDA'
        BDE = 'bde', 'BDE'
        BDI = 'bdi', 'BDI'
        BDS = 'bds', 'BDS'

    starts_on = models.DateTimeField()
    ends_on = models.DateTimeField()
    type = models.CharField(max_length=3, choices=BDX.choices, verbose_name="Campagne")

    @property
    def school_year(self):
        if 1 <= self.starts_on.month < 9:
            return self.starts_on.year-1
        return self.starts_on.year

    def __str__(self):
        return f"Campagne {self.type.upper()} {self.starts_on.year}"


class List(models.Model):

    class Meta:
        verbose_name = "Liste"

    campaign = models.ForeignKey(Campaign, related_name="lists", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    logo = ResizedImageField(size=[500, 500], quality=90, upload_to=FilePath.logo, force_format="PNG", null=True, blank=True)
    program = models.FileField(upload_to=FilePath.program, null=True, blank=True)
    votes_binary = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.campaign.type.upper()} {self.campaign.starts_on.year}"


class Vote(models.Model):

    class Meta:
        verbose_name = "Vote"

    campaign = models.OneToOneField(Campaign, related_name="vote", on_delete=models.CASCADE)
    starts_on = models.DateTimeField()
    ends_on = models.DateTimeField()

    def __str__(self):
        return f"Campagne {self.campaign.type.upper()} {self.starts_on.year}"


class VoteUser(models.Model):

    class Meta:
        verbose_name = "Vote Campagne BDX"

    vote = models.ForeignKey(Vote, related_name="votes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="votes", on_delete=models.CASCADE)
