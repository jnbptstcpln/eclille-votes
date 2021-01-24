from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth.models import User


class Campaign(models.Model):

    class Meta:
        ordering = '-starts_on',

    class BDX(models.TextChoices):
        BDA = 'bda', 'BDA'
        BDE = 'bde', 'BDE'
        BDI = 'bdi', 'BDI'
        BDS = 'bds', 'BDS'

    starts_on = models.DateTimeField()
    ends_on = models.DateTimeField()
    type = models.CharField(max_length=3, choices=BDX.choices)

    def __str__(self):
        return f"Campagne {self.type.upper()} {self.starts_on.year}"


class List(models.Model):

    campaign = models.ForeignKey(Campaign, related_name="lists", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    logo = ResizedImageField(size=[500, 500], quality=90, upload_to='bdx_list_logo', force_format="PNG", null=True, blank=True)
    program = models.FileField(upload_to="bdx_list_program", null=True, blank=True)

    def __str__(self):
        return f"Campagne {self.campaign.type.upper()} {self.campaign.starts_on.year} - {self.name}"


class Vote(models.Model):
    campaign = models.OneToOneField(Campaign, related_name="vote", on_delete=models.CASCADE)
    starts_on = models.DateTimeField()
    ends_on = models.DateTimeField()

    def __str__(self):
        return f"Campagne {self.type.upper()} {self.starts_on.year}"


class VoteUrn(models.Model):
    vote = models.ForeignKey(Vote, related_name="urns", on_delete=models.CASCADE)
    list = models.OneToOneField(List, related_name="urn", on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"Campagne {self.campaign.type.upper()} {self.campaign.starts_on.year} - {self.list.name}"


class VoteUser(models.Model):
    vote = models.ForeignKey(Vote, related_name="votes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="votes", on_delete=models.CASCADE)
