# Create your models here.
import pathlib
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
#from django.utils.safestring import mark_safe
#from django_resized import ResizedImageField
#from colorfield.fields import ColorField

TARGET_TYPE = [
    ("", "----"),
    ("_blank", _("New window")),
    ("_self", _("Same frame")),
    ("_parent", _("Parent frame")),
    ("_top", _("Full body")),  
]


class Application(models.Model):
    name = models.CharField(_("Name"), help_text=_("Django: name of application installed"), unique=True, max_length=32, null=True, blank=False)
    path = models.SlugField(_("Template pathname"), help_text=_("Template pathname or app_name from url.py"), max_length=32, null=True, blank=True)
    is_app = models.BooleanField(_("Is registered"), help_text=_("Django: app_name is registerd in url.py"), default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _("Django application")
        verbose_name_plural = _("Django Applications")

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        self.path =slugify(self.path)
        super().save(*args, **kwargs)

    @property
    def appname(self):
        return self.app_name

    def __str__(self):
        return f'{self.name}'


class Icon(models.Model):
    label = models.CharField(_("Icon name"), max_length=100, null=True, )
    html = models.CharField(_("Icon Awesome or img"), help_text=_("Free font Awesome or img html representation"), max_length=128, null=True, blank=False)

    class Meta:
        ordering = ['label', ]
        verbose_name = _("Icon Awesome or img")
        verbose_name_plural = _("Icons Awesome or img")

    def __str__(self):
        return f'{self.label}'


class SensorGroup(models.Model):
    name = models.SlugField(_("Sensor group"), help_text=_("Max 32 chars long"), unique=True, max_length=32, null=True, blank=False)
    title = models.CharField(_("Short description"), max_length=64, null=True, blank=True)
    selection = models.BooleanField(_("Visible in filter selection"), default=False)
    active = models.BooleanField(_("Active"), help_text=_("Active by default in group selection"), default=False)

    class Meta:
        ordering = ['name']
        verbose_name = _("Sensor group")
        verbose_name_plural = _("Sensors group")

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class Location(models.Model):
    SHAPE = [
        ("default", _("All region")),
        ("circle", _("Circle")),
        ("rect", _("Rectangle")),
        ("poly", _("Polygone")),
    ]
    name = models.CharField(_("Location"), max_length=64, null=True, blank=True)
    flat = models.SmallIntegerField(_("Flat"), null=True, blank=True, default=0)
    area_shape = models.CharField(_("Area shape"), choices=SHAPE, max_length=8, null=True, blank=True, default='circle')
    area_coords = models.CharField(_("Area coords"), max_length=200, null=True, blank=True, default='')
    area_href =  models.CharField(_("Area href"), max_length=100, null=True, blank=True, default='')
    area_onclick = models.CharField(_("Area onclick js"), max_length=64, null=True, blank=True, default='')
    selection = models.BooleanField(_("Visible"), help_text=_("Visible in the filter of selection"), default=True)
    active = models.BooleanField(_("Active"), help_text=_("Active by default in location selection"), default=True)
    
   
    
    class Meta:
        ordering = ['name']
        verbose_name = _("Location")
        verbose_name_plural =  _("Locations")


    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


class TemplatePage(models.Model):
    name = models.CharField(_("Name"), help_text=_("Template name"), max_length=100, unique=True, null=True, blank=True)
    title = models.CharField(_("Short description"), max_length=64, null=True, blank=True)
    htmlpath = models.CharField(_("Html page"), help_text=_("Path to html template page name"), max_length=100, null=True, blank=True)  
    app = models.ForeignKey(Application, verbose_name=_("Application"), on_delete=models.CASCADE, null=True, blank=False, )
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")

    def set_template_model(self):
        filename = settings.DASHBOARD_TEMPLATES_ROOT / f'{self.name}.html'
        if not pathlib.Path(filename).is_file():
            with open(filename, 'w') as f:
                f.writelines([
                    "{% extends 'board-base.html' %}\n",
                    "{% load i18n apptags boardtags %}\n",
                    "{% block menubar %}{% endblock %}\n",
                    "{% block content %}{% endblock %}\n",
                ])

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        self.htmlpath = f'{self.name}.html'
        if self.app.path:
            self.htmlpath = f'{self.app.path}/{self.htmlpath}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.app.name}: {self.name}'


@receiver(post_save, sender=TemplatePage)
def update_dashboard(sender, instance, created, **kwargs):  # @UnusedVariable
    if created:
        instance.set_template_model()

  
class UrlBase(models.Model):
    name = models.CharField(_("Name"), help_text=_("Route base name"), max_length=100, unique=True, null=True, blank=True)
    title = models.CharField(_("Short description"), max_length=64, null=True, blank=True)
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Route base")
        verbose_name_plural = verbose_name
          
    def __str__(self):
        return f'{self.name}: {self.title}'        
        
        
class NavPane(models.Model):
    label = models.CharField(_("Navigation pane"), help_text=_("Navigation pane label"), max_length=100, null=True, )
    title = models.CharField(_("Menu title"), max_length=64, null=True, blank=True)
    icon = models.ForeignKey(Icon, verbose_name=_("Icon Awesome"), on_delete=models.CASCADE, null=True, blank=False, )
    index = models.BooleanField(_("Is index"), help_text=_('Is a page index'), default=False)
    # links
    urlbase = models.ForeignKey(UrlBase, verbose_name=_("Url route base"), on_delete=models.CASCADE, null=True, blank=False, )
    page = models.CharField(_("Code page"), help_text=_("Code page (64 chars long)"), unique=True, max_length=64, null=True, blank=True)
    link = models.CharField(_("Link"), help_text=_('Link as /board/codepage/sensorgroup'), max_length=128, null=True, blank=True, default='main')
    # dependencies
    template = models.ForeignKey(TemplatePage, verbose_name=_("Template"), on_delete=models.CASCADE, blank=False, null=True, help_text=_("Template name"))
    group = models.ForeignKey(SensorGroup, verbose_name=_("Sensor group"), on_delete=models.CASCADE, null=True, blank=True, help_text=_('If Url Pattern group considered'))
    location = models.ForeignKey(Location, verbose_name=_("Location"), on_delete=models.CASCADE, null=True, blank=True, help_text=_('If Url Pattern location considered'))    
    url = models.CharField(_("Url target"), help_text=_('Url target for iframe'), max_length=128, null=True, blank=True, default='')
    target = models.CharField(_("Link: Target tag"), choices=TARGET_TYPE, max_length=32, null=True, blank=True, default='')
    options = models.CharField(_("Link: Options tag"), help_text=_('Example: onclick="func($(this))"'), max_length=128, null=True, blank=True, default='')        
    # display
    tab = models.SmallIntegerField(_("Tab"), null=True, blank=True, default=0)
    order = models.PositiveSmallIntegerField(_("Order"), help_text=_('Position in navigation pane'), null=True, blank=True, default=0)
    position = models.PositiveSmallIntegerField(_("Position in pane "), help_text=_('upper: 1, bottom: 0'), null=True, blank=True, default=1)
    show = models.BooleanField(_("Show"), help_text=_('Show in navigation pane '), default=True)
    active = models.BooleanField(_("Active"), help_text=_('Active in navigation pane '), default=True)

    class Meta:
        ordering = ['tab', 'order', 'page']
        verbose_name = _("Navigation pane")
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        slug = self.page if self.page else self.title
        self.page = slugify(slug)
        
        self.link = ''
        if self.template.app.is_app: # is registered
            self.link = f'/{self.template.app.name}'
            
        self.link += f'/{self.urlbase.name}/{self.page}/'
        if self.group and self.location:
            self.link += f'{self.group.name}/{self.location.name}/'  
        elif self.group:
            self.link += f'{self.group.name}/'
        elif self.location:
            self.link += f'{self.location.name}/'
            
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.label}'


class SshTunnel(models.Model):
    label = models.CharField(_("Tunnel name"), unique=True, max_length=100, null=True, blank=False)
    host = models.CharField(_("Ssh host server"), max_length=128, blank=False, null=True, default='127.0.0.1')
    port = models.IntegerField(_("ssh host port server"), null=True, blank=True, default=22)
    username = models.CharField(_("Ssh username"), max_length=128, blank=True, null=True, default=None)
    password = models.CharField(_("Ssh password"), max_length=64, blank=True, null=True, default=None)

    remote_bind_host = models.CharField(_("Remote bind host"), max_length=128, blank=False, null=True, default='127.0.0.1')
    remote_bind_port = models.IntegerField(_("Remote bind host port"), null=True, blank=True, default=80)

    local_bind_host = models.CharField(_("Local bind host"), max_length=128, blank=False, null=True, default='127.0.0.1')
    local_bind_port = models.IntegerField(_("Local bind host port"), null=True, blank=True, default=8080)
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ['label']
        verbose_name = _("Ssh tunnel host")
        verbose_name_plural =  _("Ssh tunnel hosts")


    def __str__(self):
        return f'{self.host:{self.port}}'

