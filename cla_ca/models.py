import os
import uuid

from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

from cla_votes.const import CURSUS_CENTRALE, CURSUS_ITEEM
from cla_auth.models import UserInfos


class FilePath:

    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split('.')[-1]
        filename = "%s-%s.%s" % (slugify(f"{instance.first_name} {instance.last_name}"), uuid.uuid4(), ext)
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def photo(cls, instance, filename):
        return cls._path(instance, ["cla_ca", "photo"], filename)


class ElectionManager(models.Manager):

    def ongoing(self):
        return self.filter(starts_on__lt=timezone.now(), ends_on__gt=timezone.now()).last()


class Election(models.Model):

    objects = ElectionManager()

    class Meta:
        ordering = '-starts_on',
        verbose_name = "Election"

    starts_on = models.DateTimeField(verbose_name="Début de l'élection")
    ends_on = models.DateTimeField(verbose_name="Fin de l'élection")

    @property
    def school_year(self):
        if 1 <= self.starts_on.month < 9:
            return self.starts_on.year-1
        return self.starts_on.year

    def should_display_vote(self):
        return self.starts_on <= timezone.now() < self.ends_on

    def did_user_vote(self, user: User):
        return self.votes.filter(user=user).count() > 0

    def register_user(self, user: User):
        VoteUser.objects.create(
            vote=self,
            college=user.infos.college,
            user=user
        )

    @property
    def candidates_by_colleges(self):
        colleges = {}
        for college in UserInfos.Colleges.values:
            colleges[college] = {
                'candidates': Candidate.objects.filter(election=self, college=college).order_by("college", "first_name"),
                'blank_votes': self.blank_votes(college),
                'total_votes': self.total_votes(college),
            }
        return colleges

    @property
    def candidates_by_colleges_result(self):
        colleges = {}
        for college in UserInfos.Colleges.values:
            colleges[college] = {
                'candidates': Candidate.objects.filter(election=self, college=college).order_by("votes"),
                'blank_votes': self.blank_votes(college),
                'total_votes': self.total_votes(college),
            }
        return colleges

    def blank_votes(self, college):
        total = self.votes.filter(college=college).count()*2
        for candidate in self.candidates.filter(college=college):
            total -= candidate.votes
        return total

    def total_votes(self, college=None):
        if college is not None:
            return self.votes.filter(college=college).count()*2
        return self.votes.count()*2

    def total_voters(self):
        return self.votes.count()

    @property
    def participation_stats(self):
        participation_stats = {c: 0 for c in CURSUS_ITEEM + CURSUS_CENTRALE}

        total = 0
        for c in participation_stats.keys():
            count = self.votes.filter(user__infos__cursus=c).count()
            participation_stats[c] = count
            total += count
        participation_stats['Autre'] = self.total_votes()//2 - total

        return participation_stats

    def __str__(self):
        return f"Elections CA {self.school_year}/{self.school_year+1}"


class Candidate(models.Model):

    class Meta:
        verbose_name = "Candidat"
        #ordering = "college", "last_name"

    election = models.ForeignKey(Election, related_name="candidates", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    cover_letter = models.TextField(verbose_name="Lettre de motivation")
    college = models.CharField(max_length=10, choices=UserInfos.Colleges.choices, verbose_name="Collège électoral")
    photo = ResizedImageField(size=[300, 300], quality=80, upload_to=FilePath.photo, force_format="JPEG", null=True, blank=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class VoteUser(models.Model):

    class Meta:
        verbose_name = "Vote Elections CA"

    vote = models.ForeignKey(Election, related_name="votes", on_delete=models.CASCADE)
    college = models.CharField(max_length=10, choices=UserInfos.Colleges.choices)
    user = models.ForeignKey(User, related_name="votes_ca", on_delete=models.CASCADE)
    voted_on = models.DateTimeField(auto_now=True, null=True)
