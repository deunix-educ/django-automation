'''
Created on 24 déc. 2020

@author: denis
'''
import logging
from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import LoggedInUser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    LoggedInUser.objects.get_or_create(user_id=user.id)
    ip = request.META.get('REMOTE_ADDR')
    logger.info(f'[DJANGO] login user: {user} via ip: {ip}')



@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    LoggedInUser.objects.filter(user_id=user.id).delete()
    ip = request.META.get('REMOTE_ADDR')
    logger.info(f'[DJANGO] logout user: {user} via ip: {ip}')


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    logger.error(f'[DJANGO] login failed for: {ip} {credentials}')


