#
# encoding: utf-8
#import json
#from django.utils.translation import gettext_lazy as _
#from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.functional import Promise
from django.utils.encoding import force_str
from django.core.serializers.json import DjangoJSONEncoder
from celery import shared_task


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_str(obj)
        return super(LazyEncoder, self).default(obj)


@shared_task
def async_send_mail(subject, body, from_email, to=[], bcc=[], cc=[], html=None, fail_silently=False, attachments=[],  connection=None):
    msg = EmailMultiAlternatives(subject, body, from_email, to, bcc=bcc, cc=cc, connection=connection)
    if html:
        msg.attach_alternative(html, 'text/html')
    for f in attachments:
        msg.attach_file(f)
    msg.send(fail_silently)


def host_site_url():
    site = Site.objects.filter(id=settings.SITE_ID).first()
    return '{}{}'.format(settings.DEFAULT_HTTP_PROTOCOL, site.domain)


def send_mail(to, template, context, request={}):
    context.update({'request': request})

    protocol=settings.DEFAULT_HTTP_PROTOCOL
    if protocol == 'https':
        uri = context.get('uri')
        if uri:
            context['uri'] = uri.replace('http://', 'https://')

    html_content = render_to_string(f'{template}.html', context)
    text_content = render_to_string(f'{template}.txt', context)

    from_email = settings.DEFAULT_FROM_EMAIL
    if request:
        from_email = context['owner'].email

    if not to:
        to = [settings.DEFAULT_TO_EMAIL]

    if type(to) is not list:
        to = [to]

    attachments = context.pop('attachments', [])
    subject, text =  context['subject'], text_content
    async_send_mail(subject, text, from_email, to, fail_silently=False, html=html_content, attachments=attachments)

    #print("async_send_mail.........", to, subject)


