# encoding: utf-8
from __future__ import unicode_literals
#import json
from time import strftime
from datetime import datetime
from django.db import models
from django import forms
from django.utils.timezone import now as timezone_now
from django.utils.translation import gettext_lazy as _


class DatePickerInput(forms.DateInput):
    input_type = 'date'


class TimePickerInput(forms.TimeInput):
    input_type = 'time'


class DateTimePickerInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class DateMixin(models.Model):
    """
    Abstract base class with a creation and modification date and time
    """
    created = models.DateTimeField(_("date time creation"), editable=False,)
    modified = models.DateTimeField(_("Datetime modification"), null=True, editable=False,)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = timezone_now()
        else:
            # To ensure that we have a creation data always, we add this one
            if not self.created:
                self.created = timezone_now()
            self.modified = timezone_now()

        super(DateMixin, self).save(*args, **kwargs)

    save.alters_data = True

    class Meta:
        abstract = True


class UnixTimestampField(models.DateTimeField):
    """UnixTimestampField: creates a DateTimeField that is represented on the
    database as a TIMESTAMP field rather than the usual DATETIME field.
    """
    def __init__(self, null=False, blank=False, **kwargs):
        super(UnixTimestampField, self).__init__(**kwargs)
        # default for TIMESTAMP is NOT NULL unlike most fields, so we have to
        # cheat a little:
        self.blank, self.isnull = blank, null
        self.null = True # To prevent the framework from shoving in "not null".


    def db_type(self, connection):
        typ=['TIMESTAMP']
        # See above!
        if self.isnull:
            typ += ['NULL']
        if self.auto_created:
            typ += ['default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP']
        return ' '.join(typ)


    def to_python(self, value):
        if isinstance(value, int):
            return datetime.fromtimestamp(value)
        else:
            return models.DateTimeField.to_python(self, value)


    def get_db_prep_value(self, value, connection, prepared=False):
        if value==None:
            return None
        # Use '%Y%m%d%H%M%S' for MySQL < 4.1
        return strftime('%Y-%m-%d %H:%M:%S',value.timetuple())

