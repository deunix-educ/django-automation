#
# encoding: utf-8
#import sys
#import os, pathlib

#from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            User = get_user_model()
            if User.objects.count() == 0:
                for email, username, password, is_superuser in settings.ADMINS:
                    if is_superuser:
                        User.objects.create_superuser(
                            email=email,
                            username=username,
                            password=password,
                            is_active=True,
                            is_superuser=is_superuser,
                        )
                    else:
                        User.objects.create_user(
                            email=email,
                            username=username,
                            password=password,
                            is_active=True,
                        )
                    print(f'Creating {username} user with {password} password and email: {email} superuser: {is_superuser}')

        except Exception as e:
            print(f'Creating superuser  error {e}')
