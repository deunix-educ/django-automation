#
# encoding: utf-8
#import subprocess, os
import logging, requests
import urllib.parse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from celery import shared_task

logger = logging.getLogger(__name__)


def supervisor_ctl(**kwargs):
    params = urllib.parse.urlencode(kwargs, doseq=True)
    url = f'http://{settings.SUPERVISOR_USERNAME}:{settings.SUPERVISOR_PASSWORD}@{settings.SUPERVISOR_HOSTNAME}:{settings.SUPERVISOR_HOSTPORT}?{params}'
    requests.get(url=url)
    

def async_send_mail(subject, body, from_email, to=[], bcc=[], cc=[], html=None, fail_silently=False, attachments=[],  connection=None):
    msg = EmailMultiAlternatives(subject, body, from_email, to, bcc=bcc, cc=cc, connection=connection)
    if html:
        msg.attach_alternative(html, 'text/html')
    for f in attachments:
        msg.attach_file(f)

    msg.send(fail_silently)
    
@shared_task
def send_mail(subject, text, to=None, attachments=None):
    from_email = settings.DEFAULT_FROM_EMAIL
    if not to:
        to = [settings.EMAIL_HOST_USER]
    if type(to) is not list:
        to = [to]       
    async_send_mail(subject, text, from_email, to, attachments=attachments)
    
    
@shared_task
def supervisor(app='automation', mode='restart', srv="master"):
    try:
        service = f'{app}:{srv}'
        supervisor_ctl(processname=service, action=mode)
        logger.info(f"{mode} {service}")
    except Exception as e:
        logger.error(f"supervisor {mode} task  error {e}")

