import re

from django.db import models
from django.contrib.auth.models import User
from cla_votes.utils import current_school_year


class UserInfos(models.Model):
    """
    The UserInfo model extends user by adding new properties
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="infos")
    cursus = models.CharField(max_length=100, null=True)
    promo = models.IntegerField()

    class School(models.TextChoices):
        CENTRALE = "centrale", "CENTRALE"
        ITEEM = "iteem", "ITEEM"
        ENSCL = "enscl", "ENSCL"
        OTHER = "other", "OTHER"

    class Colleges(models.TextChoices):
        G1 = "g1", "G1"
        G2 = "g2", "G2"
        G3 = "g3", "G3"
        IE1 = "ie1"
        IE2 = "ie2"
        IE3_IE4_IE5 = "ie3/ie4/ie5", "IE3/IE4/IE5"
        CH1 = "ch1", "CH1"
        CH2 = "ch2", "CH2"
        ENSCL = "ENSCL", "ENSCL"  # Deprecated
        IE1_IE2 = "ie1/ie2", "IE1/IE2"  # Deprecated
        IE3 = "ie3", "IE3"  # Deprecated
        IE4 = "ie4", "IE4"  # Deprecated
        IE5 = "ie5", "IE5"  # Deprecated

    def is_from_centrale(self):
        return re.match(r"^G\d.*", self.cursus)

    def is_from_iteem(self):
        return re.match(r"^IE\d.*", self.cursus)

    def is_from_enscl(self):
        return re.match(r"^CH\d.*", self.cursus) or re.match(r"^CPI\d.*", self.cursus)

    @property
    def school(self):
        if self.is_from_centrale():
            return self.School.CENTRALE
        elif self.is_from_iteem():
            return self.School.ITEEM
        elif self.is_from_enscl():
            return self.School.ENSCL
        else:
            return self.School.OTHER

    @property
    def college(self):
        colleges = [
            {
                self.School.CENTRALE: self.Colleges.G3,
                self.School.ITEEM: self.Colleges.IE3_IE4_IE5,
                self.School.ENSCL: self.Colleges.CH2,
            },
            {
                self.School.CENTRALE: self.Colleges.G2,
                self.School.ITEEM: self.Colleges.IE3_IE4_IE5,
                self.School.ENSCL: self.Colleges.CH2,
            },
            {
                self.School.CENTRALE: self.Colleges.G1,
                self.School.ITEEM: self.Colleges.IE3_IE4_IE5,
                self.School.ENSCL: self.Colleges.CH1,
            },
            {
                self.School.CENTRALE: self.Colleges.G1,
                self.School.ITEEM: self.Colleges.IE2,
                self.School.ENSCL: self.Colleges.CH1,
            },
            {
                self.School.CENTRALE: self.Colleges.G1,
                self.School.ITEEM: self.Colleges.IE1,
                self.School.ENSCL: self.Colleges.CH1,
            },
        ]

        if self.promo <= current_school_year() + 1:
            return colleges[0].get(self.school)
        elif self.promo == current_school_year() + 2:
            return colleges[1].get(self.school)
        elif self.promo == current_school_year() + 3:
            return colleges[2].get(self.school)
        elif self.promo == current_school_year() + 4:
            return colleges[3].get(self.school)
        elif self.promo == current_school_year() + 5:
            return colleges[4].get(self.school)

    @property
    def college_before(self):
        colleges = [
            {
                self.School.CENTRALE: self.Colleges.G3,
                self.School.ITEEM: self.Colleges.IE3_IE4_IE5,
                self.School.ENSCL: self.Colleges.CH2,
            },
            {
                self.School.CENTRALE: self.Colleges.G2,
                self.School.ITEEM: self.Colleges.IE3_IE4_IE5,
                self.School.ENSCL: self.Colleges.CH2,
            },
            {
                self.School.CENTRALE: self.Colleges.G1,
                self.School.ITEEM: self.Colleges.IE3_IE4_IE5,
                self.School.ENSCL: self.Colleges.CH1,
            },
            {
                self.School.CENTRALE: self.Colleges.G1,
                self.School.ITEEM: self.Colleges.IE2,
                self.School.ENSCL: self.Colleges.CH1,
            },
            {
                self.School.CENTRALE: self.Colleges.G1,
                self.School.ITEEM: self.Colleges.IE1,
                self.School.ENSCL: self.Colleges.CH1,
            },
        ]

        if self.promo <= current_school_year():
            return colleges[0].get(self.school)
        elif self.promo == current_school_year() + 1:
            return colleges[1].get(self.school)
        elif self.promo == current_school_year() + 2:
            return colleges[2].get(self.school)
        elif self.promo == current_school_year() + 3:
            return colleges[3].get(self.school)
        elif self.promo == current_school_year() + 4:
            return colleges[4].get(self.school)
