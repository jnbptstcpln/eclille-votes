from django.db import models
from django.utils import timezone


class User(models.Model):

    class Meta:
        verbose_name = "Etudiant"

    email = models.EmailField(unique=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    email_sent_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email


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
            return self.starts_on.year - 1
        return self.starts_on.year

    def results(self):
        results = {}
        for vote in self.votes.all():
            for pole, item in vote.content.items():
                if pole not in results.keys():
                    results[pole] = {}
                if item not in results[pole].keys():
                    results[pole][item] = 0
                results[pole][item] += 1
        return results

    def did_user_vote(self, user: User):
        return self.votes.filter(user=user).count() > 0

    def __str__(self):
        return f"Elections ENSCL {self.school_year}/{self.school_year+1}"


class UserVote(models.Model):
    user = models.ForeignKey(User, related_name="votes", on_delete=models.CASCADE)
    election = models.ForeignKey(Election, related_name="votes", on_delete=models.CASCADE)
    voted_on = models.DateTimeField(auto_now=True)
    content = models.JSONField()
