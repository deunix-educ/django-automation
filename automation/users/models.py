#
# encoding: utf-8
#from django.conf import settings
#from django.dispatch import receiver
#from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.safestring import mark_safe
from django_resized import ResizedImageField



class HomeSite(models.Model):
    name  = models.CharField(_("Home site name"), max_length=64, null=True, blank=True)
    photo = ResizedImageField(_("Picture site"), size=[640, 480], upload_to='photos/', null=True, blank=True, default = 'photos/no-image.png')
    adr1   = models.CharField(_("Address 1"), max_length=64, null=True, blank=True)
    adr2   = models.CharField(_("Address 2"), max_length=64, null=True, blank=True)
    zip    = models.CharField(_("Zip code"), max_length=6, null=True, blank=True)
    city   = models.CharField(_("City"), max_length=64, null=True, blank=True)

    lat = models.CharField("Latitude", max_length=16, null=True, blank=False, default='NaN')
    lon = models.CharField("Lontitude", max_length=16, null=True, blank=False, default='NaN')
    alt = models.CharField(_("Altitude"), max_length=16, null=True, blank=False, default='NaN')
    min_zoom = models.IntegerField(_("Zoom minimum"), help_text=_("Leaflet Zoom minimum"), null=True, blank=True, default=6)
    max_zoom = models.IntegerField(_("Zoom maximum"), help_text=_("Leaflet Zoom maximum"), null=True, blank=True, default=18)

    def photo_tag(self):
        photo = self.photo.url
        if not self.photo:
            photo = "/static/img/no-img.png"
        return mark_safe('<img src="%s" style="width: 45px; height:45px;">' % photo)

    photo_tag.short_description = _("Picture site")
    photo_tag.allow_tags = True


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Home site")
        verbose_name_plural = _("Homes site")

## User
class User(AbstractUser):
    #
    homesite = models.ForeignKey(HomeSite, verbose_name=_("Home site Owner"), on_delete=models.CASCADE, null=True)
    adr1   = models.CharField(_("Address 1"), max_length=64, null=True, blank=True)
    adr2   = models.CharField(_("Address 2"), max_length=64, null=True, blank=True)
    zip    = models.CharField(_("Zip code"), max_length=6, null=True, blank=True)
    city   = models.CharField(_("City"), max_length=64, null=True, blank=True)
    mobile = models.CharField (_("Mobile phone"), max_length=32, null=True, blank=True)
    photo = ResizedImageField(_("Photo"), size=[640, 480], upload_to='img/', null=True, blank=True, default = 'img/nobody.jpg')

    
    def image_tag(self):
        photo = self.photo.url
        if not self.photo:
            photo = "/static/img/no-image.png"
        return mark_safe('<img src="%s" style="width: 45px; height:45px;">' % photo)

    image_tag.short_description = _("Photo")
    image_tag.allow_tags = True


    class Meta:
        ordering = ['email']
        verbose_name = _("User")
        verbose_name_plural = _("Users")


    def __str__(self):
        return f'{self.username}'


# Model to store the list of logged in users
class LoggedInUser(models.Model):
    user = models.OneToOneField(User, related_name='logged_in_user', on_delete=models.CASCADE, blank=True, null=True)
    # Session keys are 32 characters long
    session_key = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        verbose_name = _("Logged User")
        verbose_name_plural = _("Logged Users")

    def __str__(self):
        return f'{self.user.username}'


#
