from django.test import TestCase
from django.http import HttpRequest
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings


from featureflipper.models import Feature, enable_features, disable_features
from featureflipper.middleware import FeaturesDetector, FeaturesMiddleware

class FeatureFlipperTest(TestCase):
    """
    Tests for django-feature-flipper
    """
    def setUp(self):

        self.feature = Feature.objects.create(name='fftestfeature')
        self.feature_enabled = Feature.objects.create(name='fftestfeature_enabled', enabled = True)

        self.user = User.objects.create_user('fftestuser', '', 'password')

        self.client = Client()
        self.assertTrue(self.client.login(username='fftestuser', password='password'))

    def test_middleware(self):
        """Test features object is correctly set on request.
        No features are enabled
        """

        response = self.client.get('/')

        self.assertTrue('features' in response.context)
        self.assertTrue('fftestfeature' in response.context['features'])
        self.assertFalse(response.context['features']['fftestfeature'])

    def test_enable_feature_per_request(self):
        """Param ?enable_fftestfeature enables particular
           feature only for the current request"""
        response = self.client.get('/?enable_fftestfeature')
        self.assertTrue(response.context['features']['fftestfeature'])

        response = self.client.get('/')
        self.assertFalse(response.context['features']['fftestfeature'])

    def test_enable_feature_per_session(self):

        response = self.client.get('/?session_enable_fftestfeature')
        self.assertFalse(response.context['features']['fftestfeature'])

        perm = Permission.objects.get(codename='can_flip_with_url')
        self.user.user_permissions.add(perm)
        self.assertTrue(self.user.has_perm('featureflipper.can_flip_with_url'))

        response = self.client.get('/?session_enable_fftestfeature')

        self.assertTrue(response.context['features']['fftestfeature'])
        response = self.client.get('/')
        self.assertTrue(response.context['features']['fftestfeature'])

        response = self.client.get('/?session_clear_features')
        self.assertFalse(response.context['features']['fftestfeature'])


    def test_features_on_user_only_basis(self):
        """Pass only user to detect features
        Only Global and userprofile settings are considered"""

        features , feature_panel= FeaturesDetector().get_features(self.user)
        #assert disbaled
        self.assertFalse(features["fftestfeature"])

        up_class = models.get_model(*settings.AUTH_PROFILE_MODULE.rsplit(".", 1))
        up = up_class.objects.create(user = self.user)
        up.features_enabled = "fftestfeature"
        up.save()
        #assert enabled
        features, feature_panel = FeaturesDetector().get_features(self.user)
        self.assertTrue(features["fftestfeature"])


    def test_no_deco(self):
        self.assertFalse(Feature.objects.get(name='fftestfeature').enabled)
        self.assertTrue(Feature.objects.get(name='fftestfeature_enabled').enabled)

    @enable_features(["fftestfeature"])
    def test_anable_feature_decorator(self):
        self.assertTrue(Feature.objects.get(name='fftestfeature').enabled)

    @disable_features(['fftestfeature_enabled'])
    def test_anable_feature_decorator(self):
        self.assertFalse(Feature.objects.get(id = self.feature_enabled.id).enabled)


    def test_decorators_raise_errors(self):
        """If features does not exist decorators raise errors"""

        class A:
            @enable_features(["fftestfeature_not_existing"])
            def enable_not_existing(self):
                pass
            @disable_features(["fftestfeature_not_existing"])
            def disable_not_existing():
                pass
        a = A()
        self.assertRaises(RuntimeError, a.enable_not_existing)
        self.assertRaises(RuntimeError, a.disable_not_existing)
