import os
import math
import uuid

from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

from cla_votes.const import CURSUS_CENTRALE, CURSUS_ITEEM, CURSUS_ENSCL


class FilePath:
    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split(".")[-1]
        filename = "%s-%s.%s" % (slugify(instance.name), uuid.uuid4(), ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def program(cls, instance, filename):
        return cls._path(instance, ["cla_bdx", "program"], filename)

    @classmethod
    def logo(cls, instance, filename):
        return cls._path(instance, ["cla_bdx", "logo"], filename)

    @classmethod
    def regulation(cls, instance, filename):
        pathlist = ["cla_bdx", "regulation"]
        ext = filename.split(".")[-1]
        filename = "%s-%s.%s" % ("reglement", uuid.uuid4(), ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)


class CampaignManager(models.Manager):
    def ongoing(self, type=None):
        if type is not None:
            return self.filter(
                type=type, starts_on__lt=timezone.now(), ends_on__gt=timezone.now()
            ).last()
        return self.filter(
            starts_on__lt=timezone.now(), ends_on__gt=timezone.now()
        ).last()

    def vote_ongoing(self, type=None):
        if type is not None:
            return self.filter(
                type=type,
                vote__starts_on__lt=timezone.now(),
                vote__ends_on__gt=timezone.now(),
            ).last()
        return self.filter(
            vote__starts_on__lt=timezone.now(), vote__ends_on__gt=timezone.now()
        ).last()


class Campaign(models.Model):
    objects = CampaignManager()

    class Meta:
        ordering = ("-starts_on",)
        verbose_name = "Campagne"

    class BDX(models.TextChoices):
        BDA = "bda", "BDA"
        BDE = "bde", "BDE"
        BDI = "bdi", "BDI"
        BDS = "bds", "BDS"
        BDA_ENSCL = "bda_enscl", "BDA ENSCL"
        BDE_ENSCL = "bde_enscl", "BDE ENSCL"

    starts_on = models.DateTimeField(verbose_name="Début")
    ends_on = models.DateTimeField(verbose_name="Fin")
    type = models.CharField(max_length=16, choices=BDX.choices, verbose_name="Campagne")

    @property
    def school_year(self):
        if 1 <= self.starts_on.month < 9:
            return self.starts_on.year - 1
        return self.starts_on.year

    def should_display_lists(self):
        return timezone.now() >= self.starts_on

    def should_display_vote(self):
        if not self.vote:
            return False
        return self.vote.starts_on <= timezone.now() < self.vote.ends_on

    def should_display_result(self):
        if not self.vote:
            return False
        return self.vote.display_result_on < timezone.now()

    def should_display_calendar(self):
        return self.ends_on > timezone.now()

    def can_user_vote(self, user: User):
        if self.type == Campaign.BDX.BDI:
            if user.infos.is_from_iteem():
                return True
        if self.type == Campaign.BDX.BDE:
            if user.infos.is_from_centrale():
                return True
        if self.type == Campaign.BDX.BDA:
            checks = [
                user.infos.is_from_centrale(),
                user.infos.is_from_iteem(),
                user.infos.is_from_enscl(),
            ]
            if any(checks):
                return True
        if self.type == Campaign.BDX.BDS:
            checks = [
                user.infos.is_from_centrale(),
                user.infos.is_from_iteem(),
                user.infos.is_from_enscl(),
            ]
            if any(checks):
                return True
        if self.type in {Campaign.BDX.BDA_ENSCL, Campaign.BDX.BDE_ENSCL}:
            if user.infos.is_from_enscl():
                return True

        return False

    def did_user_vote(self, user: User):
        return self.vote.votes.filter(user=user).count() > 0

    @property
    def calendar_starts_on(self):
        return self.starts_on

    @property
    def calendar_ends_on(self):
        return self.ends_on + timezone.timedelta(days=1)

    def __str__(self):
        return f"{self.type.upper()} {self.school_year}/{self.school_year+1}"


class List(models.Model):
    class Meta:
        verbose_name = "Liste"
        ordering = ("name",)

    campaign = models.ForeignKey(
        Campaign, related_name="lists", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100, verbose_name="Nom")
    logo = ResizedImageField(
        size=[500, 500],
        quality=90,
        upload_to=FilePath.logo,
        force_format="PNG",
        null=True,
        blank=True,
    )
    program = models.FileField(
        upload_to=FilePath.program, null=True, blank=True, verbose_name="Programme"
    )
    penality = models.FloatField(
        default=0, verbose_name="Pourcentage de voix de pénalité"
    )
    votes_binary = models.IntegerField(default=0)

    @property
    def votes_binary_final(self):
        return self.votes_binary - math.ceil(
            self.campaign.vote.total_votes * self.penality * 0.01
        )

    def vote_penality(self):
        return math.ceil(self.campaign.vote.total_votes * self.penality * 0.01)

    def __str__(self):
        return f"{self.name} - {self.campaign.type.upper()} {self.campaign.school_year}/{self.campaign.school_year+1}"


class Vote(models.Model):
    class Meta:
        verbose_name = "Vote"

    campaign = models.OneToOneField(
        Campaign, related_name="vote", on_delete=models.CASCADE
    )
    starts_on = models.DateTimeField(verbose_name="Début")
    ends_on = models.DateTimeField(verbose_name="Fin")
    display_result_on = models.DateTimeField(verbose_name="Publication des résultats")

    def register_user(self, user: User):
        VoteUser.objects.create(vote=self, user=user)

    @property
    def blank_votes(self):
        total = self.votes.count()
        for list in self.campaign.lists.all():
            total -= list.votes_binary
        return total

    @property
    def total_votes(self):
        return self.votes.count()

    @property
    def winner(self):
        if self.ends_on > timezone.now():
            return None

        score, winner = -1, None
        for list in self.campaign.lists.all():
            if list.votes_binary_final > score:
                score, winner = list.votes_binary_final, list
            elif list.votes_binary_final == score:
                winner = None
        return winner

    @property
    def participation_stats(self):
        participation_stats = {}

        if self.campaign.type == Campaign.BDX.BDI:
            participation_stats = {c: 0 for c in CURSUS_ITEEM}
        if self.campaign.type == Campaign.BDX.BDE:
            participation_stats = {c: 0 for c in CURSUS_CENTRALE}
        if self.campaign.type == Campaign.BDX.BDA:
            participation_stats = {
                c: 0 for c in CURSUS_CENTRALE + CURSUS_ITEEM + CURSUS_ENSCL
            }
        if self.campaign.type == Campaign.BDX.BDS:
            participation_stats = {
                c: 0 for c in CURSUS_CENTRALE + CURSUS_ITEEM + CURSUS_ENSCL
            }
        if self.campaign.type in {Campaign.BDX.BDA_ENSCL, Campaign.BDX.BDE_ENSCL}:
            participation_stats = {c: 0 for c in CURSUS_ENSCL}

        total = 0
        for c in participation_stats.keys():
            count = self.votes.filter(user__infos__cursus=c).count()
            participation_stats[c] = count
            total += count
        participation_stats["Autre"] = self.total_votes - total

        return participation_stats

    def __str__(self):
        return f"{self.campaign.type.upper()} {self.campaign.school_year}/{self.campaign.school_year+1}"


class VoteUser(models.Model):
    class Meta:
        verbose_name = "Vote Campagne BDX"

    vote = models.ForeignKey(Vote, related_name="votes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="votes", on_delete=models.CASCADE)
    voted_on = models.DateTimeField(auto_now=True, null=True)


class CampaignRegulationManager(models.Manager):
    pass


class CampaignRegulation(models.Model):
    objects = CampaignRegulationManager()

    class Meta:
        verbose_name = "Règlement des campagnes"

    voted_on = models.DateField(verbose_name="Voté le")
    file = models.FileField(
        upload_to=FilePath.regulation, null=True, blank=True, verbose_name="Fichier PDF"
    )

    @property
    def school_year(self):
        if 1 <= self.voted_on.month < 9:
            return self.voted_on.year - 1
        return self.voted_on.year

    def __str__(self):
        return f"Réglement des campagnes {self.school_year}/{self.school_year+1}"
