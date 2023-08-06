__author__ = 'Luis'
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import post_syncdb
from django.dispatch import receiver
import configure
import models


User = get_user_model()


@receiver(post_syncdb, sender=models, dispatch_uid='group:ban', weak=False)
def setup_ban_users(**kwargs):
    """
    Setup the special users required for the ban feature.
    """

    if not issubclass(User, AbstractBaseUser):
        raise ImproperlyConfigured("Class %s (AUTH_USER_MODEL) does not specify a valid User class" % User.__name__)
    for s in models.SPECIAL_USERS:
        user, saved = configure.create_special_user(User, s)
        user.set_unusable_password()
        user.save()