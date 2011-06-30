from django.contrib.auth.models import User
from test_app.models import UserProfile
from featureflipper import FeatureProvider

class UserProfileFeatures(FeatureProvider):
    source = 'userprofile'

    @staticmethod
    def features(request_or_user = None):
        if not request_or_user :
            return []
        if isinstance(request_or_user, User):
            user = request_or_user
        else:
            user = request_or_user.user

        try:
            user_profile = user.get_profile()
        except (AttributeError, UserProfile.DoesNotExist):
            return []
        else:
            return user_profile.get_features()

