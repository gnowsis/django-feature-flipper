from django.db import models
from functools import wraps

class Feature(models.Model):
    name = models.CharField(max_length=40, db_index=True, unique=True,
        help_text="Required. Used in templates (eg {% feature search %}) and URL parameters.")
    description = models.TextField(max_length=400, blank=True)
    enabled = models.BooleanField(default=False)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def flip(self):
        self.enabled = not self.enabled

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        permissions = (
            ("can_flip_with_url", "Can flip features using URL parameters"),
        )

    @property
    def status(self):
        return "enabled" if self.enabled else "disabled"

def enable_features(features = [], raise_error_on_missing=True):
    """Make sure all features required for test are enabled on site level."""
    def outter_wrapper(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if( raise_error_on_missing and
                len(features) != Feature.objects.filter(name__in = features).count()):
                raise RuntimeError("Trying to enable not existing features!!!")
            Feature.objects.filter(name__in = features).update(enabled=True)
            return f(self, *args, **kwargs)
        return wrapper
    return outter_wrapper

def disable_features(features = [], raise_error_on_missing=True):
    """Make sure all features required for test are disabled on site level."""
    def outter_wrapper(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if(raise_error_on_missing
               and len(features) != Feature.objects.filter(name__in = features).count()):
                raise RuntimeError("Trying to disable not existing features!!!")
            Feature.objects.filter(name__in = features).update(enabled=False)
            return f(self, *args, **kwargs)
        return wrapper
    return outter_wrapper
