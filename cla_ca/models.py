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
        return cls._path(instance, ["cla_ca", "photo"], filename)


class ElectionManager(models.Manager):
    def ongoing(self):
        return self.filter(
            starts_on__lt=timezone.now(), ends_on__gt=timezone.now()
        ).last()


class Election(models.Model):
    objects = ElectionManager()

    VOTE_MODE_SIMPLE = "simple"
    VOTE_MODE_CONDORCET = "condorcet"
    VOTE_MODE_CHOICES = (
        (VOTE_MODE_SIMPLE, "Vote classique (2 voix)"),
        (VOTE_MODE_CONDORCET, "Vote Condorcet (Schulze)"),
    )

    class Meta:
        ordering = ("-starts_on",)
        verbose_name = "Election"

    starts_on = models.DateTimeField(verbose_name="Début de l'élection")
    ends_on = models.DateTimeField(verbose_name="Fin de l'élection")
    anticipated = models.BooleanField(verbose_name="Election anticipée", default=False)
    vote_mode = models.CharField(
        max_length=16,
        choices=VOTE_MODE_CHOICES,
        default=VOTE_MODE_SIMPLE,
        verbose_name="Mode de vote",
    )

    @property
    def school_year(self):
        if 1 <= self.starts_on.month < 9:
            return self.starts_on.year - 1
        return self.starts_on.year

    def should_display_vote(self):
        return self.starts_on <= timezone.now() < self.ends_on

    def did_user_vote(self, user: User):
        if self.vote_mode == self.VOTE_MODE_CONDORCET:
            return self.condorcet_ballots.filter(user=user).count() > 0
        return self.votes.filter(user=user).count() > 0

    def register_user(self, user: User, college):
        VoteUser.objects.create(vote=self, college=college, user=user)

    @property
    def candidates_by_colleges(self):
        colleges = {}
        for college in UserInfos.Colleges.values:
            if college in UserInfos.DEPRECATED_COLLEGES:
                continue
            colleges[college] = {
                "candidates": Candidate.objects.filter(
                    election=self, college=college
                ).order_by("college", "first_name"),
                "blank_votes": self.blank_votes(college),
                "total_votes": self.total_votes(college),
            }
        return colleges

    @property
    def candidates_by_colleges_result(self):
        colleges = {}
        for college in UserInfos.Colleges.values:
            if college in UserInfos.DEPRECATED_COLLEGES:
                continue
            colleges[college] = {
                "candidates": Candidate.objects.filter(
                    election=self, college=college
                ).order_by("-votes"),
                "blank_votes": self.blank_votes(college),
                "total_votes": self.total_votes(college),
            }
        return colleges

    def _build_condorcet_ballots(self, ballots, candidates):
        candidate_ids = [str(candidate.pk) for candidate in candidates]
        candidate_id_set = set(candidate_ids)
        payloads = []

        for ballot in ballots:
            ranked_ids = []
            for candidate_id in ballot.ranked_candidates:
                candidate_id_str = str(candidate_id)
                if (
                    candidate_id_str in candidate_id_set
                    and candidate_id_str not in ranked_ids
                ):
                    ranked_ids.append(candidate_id_str)

            remaining = [cid for cid in candidate_ids if cid not in ranked_ids]
            groups = [[cid] for cid in ranked_ids]
            if remaining:
                groups.append(remaining)
            payloads.append({"count": 1, "ballot": groups})

        return payloads

    def _normalize_condorcet_result(self, result_payload, candidates):
        if not result_payload:
            return None

        candidate_ids = [str(candidate.pk) for candidate in candidates]
        candidate_map = {str(candidate.pk): candidate for candidate in candidates}
        winner_id = result_payload.get("winner")
        winner = candidate_map.get(str(winner_id)) if winner_id is not None else None

        pairs = result_payload.get("pairs", {})
        rows = []
        for row_index, row_id in enumerate(candidate_ids):
            counts = []
            for col_id in candidate_ids:
                if row_id == col_id:
                    counts.append(None)
                else:
                    counts.append(pairs.get((row_id, col_id), 0))
            rows.append({"candidate": candidates[row_index], "counts": counts})

        ranking = self._compute_condorcet_ranking(pairs, candidate_ids, candidates)

        return {
            "winner": winner,
            "columns": candidates,
            "rows": rows,
            "ranking": ranking,
            "raw": result_payload,
        }

    def _compute_condorcet_ranking(self, pairs, candidate_ids, candidates):
        candidate_map = {str(candidate.pk): candidate for candidate in candidates}
        scores = {}
        for cand_id in candidate_ids:
            wins = 0
            for other_id in candidate_ids:
                if cand_id != other_id:
                    if pairs.get((cand_id, other_id), 0) > pairs.get((other_id, cand_id), 0):
                        wins += 1
            scores[cand_id] = wins
        
        sorted_candidates = sorted(
            [(candidate_map[cand_id], scores[cand_id]) for cand_id in candidate_ids],
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_candidates

    @property
    def condorcet_results_by_college(self):
        results = {}
        for college in UserInfos.Colleges.values:
            if college in UserInfos.DEPRECATED_COLLEGES:
                continue

            candidates = list(
                Candidate.objects.filter(election=self, college=college).order_by(
                    "first_name", "last_name"
                )
            )
            ballots = self.condorcet_ballots.filter(college=college)
            result_payload = None
            error = None

            if not candidates:
                error = "Aucun candidat."
            else:
                try:
                    from py3votecore.condorcet import CondorcetHelper
                    from py3votecore.schulze_method import SchulzeMethod
                except Exception:
                    error = "python-vote-core n'est pas disponible."
                else:
                    ballot_payloads = self._build_condorcet_ballots(
                        ballots, candidates
                    )
                    if ballot_payloads:
                        try:
                            method = SchulzeMethod(
                                ballot_payloads,
                                ballot_notation=CondorcetHelper.BALLOT_NOTATION_GROUPING,
                            )
                            result_payload = method.as_dict()
                        except Exception as exc:
                            error = str(exc)
                    else:
                        error = "Aucun bulletin."

            results[college] = {
                "candidates": candidates,
                "ballots": ballots.count(),
                "result": self._normalize_condorcet_result(
                    result_payload, candidates
                ),
                "error": error,
            }

        return results

    def get_computed_user_college(self, user: User):
        if self.anticipated:
            return user.infos.college_before
        return user.infos.college

    def blank_votes(self, college):
        total = self.votes.filter(college=college).count() * 2
        for candidate in self.candidates.filter(college=college):
            total -= candidate.votes
        return total

    def total_votes(self, college=None):
        if college is not None:
            return self.votes.filter(college=college).count() * 2
        return self.votes.count() * 2

    def total_voters(self):
        return self.votes.count()

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
        return f"Elections CA {self.school_year}/{self.school_year+1}"


class Candidate(models.Model):
    class Meta:
        verbose_name = "Candidat"
        # ordering = "college", "last_name"

    election = models.ForeignKey(
        Election, related_name="candidates", on_delete=models.CASCADE
    )
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    cover_letter = models.TextField(verbose_name="Lettre de motivation")
    college = models.CharField(
        max_length=16,
        choices=UserInfos.Colleges.choices,
        verbose_name="Collège électoral",
    )
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
        verbose_name = "Vote Elections CA"

    vote = models.ForeignKey(Election, related_name="votes", on_delete=models.CASCADE)
    college = models.CharField(max_length=16, choices=UserInfos.Colleges.choices)
    user = models.ForeignKey(User, related_name="votes_ca", on_delete=models.CASCADE)
    voted_on = models.DateTimeField(auto_now=True, null=True)


class CondorcetBallot(models.Model):
    class Meta:
        verbose_name = "Bulletin Condorcet"
        unique_together = ("election", "user")

    election = models.ForeignKey(
        Election, related_name="condorcet_ballots", on_delete=models.CASCADE
    )
    college = models.CharField(max_length=16, choices=UserInfos.Colleges.choices)
    user = models.ForeignKey(
        User, related_name="condorcet_ballots_ca", on_delete=models.CASCADE
    )
    ranked_candidates = models.JSONField()
    voted_on = models.DateTimeField(auto_now=True, null=True)
