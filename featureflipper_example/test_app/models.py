from django.db import models

# Create your models here.

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, primary_key=True)


    features_enabled = models.CharField(null=True, blank=True, max_length=255)
    features_disabled = models.CharField(null=True, blank=True, max_length=255)


    def get_features(self):
        disabled = self.features_disabled.split(',') if self.features_disabled else []
        enabled =  [x for x in (self.features_enabled.split(',')
                                if self.features_enabled else [])
                    if x and x not in disabled]

        return ([(name, True) for name in enabled] +
                [(name, False) for name in disabled if name])
