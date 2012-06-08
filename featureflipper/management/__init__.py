from django.conf import settings
from django.db.models.signals import post_syncdb
from django.core.management import call_command


import featureflipper.models as featureflipper_app
from featureflipper.models import Feature


def load_data(sender, **kwargs):
    # This doesn't respect syncdb's verbosity option
    if getattr(settings, 'TESTING', None):
        call_command('loadfeatures', interactive=False, verbosity=0)
    else:
        call_command('loadfeatures', interactive=False)
        
post_syncdb.connect(load_data, sender=featureflipper_app)
