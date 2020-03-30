from django.conf import settings
from django.db import models


GENDER_CHOICES = (
    ('1', '男性'),
    ('2', '女性'),
)


class Profile(models.Model):
    name = models.CharField("ニックネーム", max_length=1)
    gender = models.CharField("性別", max_length=2, choices=GENDER_CHOICES)
    days = models.CharField("定刻出勤",max_length=100,null=True, blank=True)
    days_late = models.CharField("遅れ出勤",max_length=100,null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)

    def __str__(self):
        return self.name
