from django.core.management.base import BaseCommand, make_option
from django.utils import simplejson
from django.conf import settings

from featureflipper.models import Feature

import os

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--override',
            action='store_true',
            dest='override',
            default=False,
            help='Overrides already existing features.'),)

    def handle(self, file='', *args, **options):
        help = 'Loads the features from the file, or the default if none is provided.'
        if file == '':
            if hasattr(settings, 'FEATURE_FLIPPER_FEATURES_FILE'):
                file = settings.FEATURE_FLIPPER_FEATURES_FILE
            else:
                print "settings.FEATURE_FLIPPER_FEATURES_FILE is not set."
                return

        verbosity = int(options.get('verbosity', 1))

        stream = open(file)
        features = simplejson.load(stream)
        loaded_features = 0
        overriden_features = 0
        for json_feature in features:
            name = json_feature['name']
            try:
                feature = Feature.objects.get(name=name)
                if not options['override']:
                    continue
                overriden_features+=1
            except Feature.DoesNotExist:
                feature = Feature()
                loaded_features+=1
            feature.name = name
            feature.description = json_feature['description']
             # Django will convert to a boolean for us
            feature.enabled = json_feature['enabled']
            feature.save()

        if verbosity > 0:
            print "Loaded %d features." % loaded_features
            print "Overridden %d features." % overriden_features
