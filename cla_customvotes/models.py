import os
import uuid

from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

from cla_votes.const import CURSUS_CENTRALE, CURSUS_ITEEM, CURSUS_ENSCL
from cla_auth.models import UserInfos


class FilePath:
    @classmethod
    def _path(cls, instance, pathlist, filename):
        ext = filename.split(".")[-1]
        filename = "%s-%s.%s" % (
            slugify(f"{instance.first_name} {instance.last_name}"),
            uuid.uuid4(),
            ext,
        )
        pathlist.append(filename)
        return os.path.join(*pathlist)

    @classmethod
    def photo(cls, instance, filename):
        return cls._path(instance, ["cla_customvotes", "photo"], filename)


class Election(models.Model):
    class Meta:
        ordering = ("-starts_on",)
        verbose_name = "Election"

    name = models.CharField(verbose_name="Nom du vote", max_length=150)
    starts_on = models.DateTimeField(verbose_name="Début de l'élection")
    ends_on = models.DateTimeField(verbose_name="Fin de l'élection")
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(
        default=False,
        verbose_name="Le vote est actif et accessible (dans le respect des dates d'ouverture)",
    )

    @property
    def school_year(self):
        if 1 <= self.starts_on.month < 9:
            return self.starts_on.year - 1
        return self.starts_on.year

    def should_access_vote(self):
        return self.starts_on <= timezone.now() < self.ends_on and self.is_active

    def has_user_proxy(self, user: User):
        return self.proxies.filter(user=user).count() > 0

    def get_user_proxy(self, user: User):
        return self.proxies.filter(user=user).first()

    def did_user_vote(self, user: User):
        return self.votes.filter(user=user).count() > 0

    def did_user_proxy_vote(self, user: User):
        return self.proxies.filter(user=user, voted_on__isnull=False).count() > 0

    def register_user(self, user: User):
        VoteUser.objects.create(vote=self, college=user.infos.college, user=user)

    @property
    def candidates_results(self):
        return self.candidates.order_by("-votes")

    @property
    def winner(self):
        best_candidate = None
        for candidate in self.candidates_results:
            if best_candidate is None:
                best_candidate = candidate
            else:
                if candidate.votes >= best_candidate.votes:
                    return None
        return best_candidate

    def blank_votes(self):
        total = self.total_votes()
        for candidate in self.candidates_results:
            total -= candidate.votes
        return total

    def total_votes(self):
        return self.votes.count() + self.total_proxies_votes()

    def total_proxies_votes(self):
        total = 0
        for proxy in self.proxies.filter(voted_on__isnull=False):
            total += proxy.total
        return total

    @property
    def participation_stats(self):
        participation_stats = {
            c: 0 for c in CURSUS_ITEEM + CURSUS_CENTRALE + CURSUS_ENSCL
        }

        total = 0
        for c in participation_stats.keys():
            count = self.votes.filter(user__infos__cursus=c).count()
            participation_stats[c] = count
            total += count
        participation_stats["Autre"] = self.total_votes() // 2 - total

        return participation_stats

    def __str__(self):
        return self.name


class Candidate(models.Model):
    class Meta:
        verbose_name = "Candidat"
        # ordering = "college", "last_name"

    election = models.ForeignKey(
        Election, related_name="candidates", on_delete=models.CASCADE
    )
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    photo = ResizedImageField(
        size=[300, 300],
        quality=80,
        upload_to=FilePath.photo,
        force_format="JPEG",
        null=True,
        blank=True,
    )
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class VoteUser(models.Model):
    class Meta:
        verbose_name = "Vote"
        ordering = ("user__last_name",)

    vote = models.ForeignKey(Election, related_name="votes", on_delete=models.CASCADE)
    college = models.CharField(max_length=10, choices=UserInfos.Colleges.choices)
    user = models.ForeignKey(
        User, related_name="votes_custom", on_delete=models.CASCADE
    )
    voted_on = models.DateTimeField(auto_now=True, null=True)


class VoteProxy(models.Model):
    class Meta:
        unique_together = (
            "vote",
            "user",
        )
        verbose_name = "Procuration"

    vote = models.ForeignKey(Election, related_name="proxies", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="votes_custom_proxies", on_delete=models.CASCADE
    )
    names = models.TextField(
        max_length=1000,
        verbose_name="Identités des procurants",
        help_text="Indiqué une personne par ligne",
    )
    voted_on = models.DateTimeField(default=None, null=True, editable=False)

    @property
    def total(self):
        return len(["" for name in self.names.split("\n") if len(name.strip()) > 0])
