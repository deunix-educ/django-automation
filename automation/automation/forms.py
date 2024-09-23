#
from django.utils.translation import gettext_lazy as _
from django import forms

from contrib.models import DateTimePickerInput

ALL_ITEMS = [('', _("All"))]

DATE_FROM = [
    ('today', _('Today')),
    ('past-2', _('Past 2 days')),
    ('past-3', _('Past 3 days')),
    ('past-4', _('Past 4 days')),
    ('past-5', _('Past 5 days')),
    ('past-6', _('Past 6 days')),
    ('week'  , _('Last 7 days')),
    ('past-8', _('Past 8 days')),
    ('past-9', _('Past 9 days')),
    ('past-10',_('Past 10 days')),
    ('week2',  _('Last 15 days')),
    ('month',  _('From 1 month')),
    ('month3', _('From 3 months')),
    ('month6', _('From 6 months')),
    ('year', _('From 1 year')),
]


class ReplyFiltersForm(forms.Form):

    lat_n = forms.CharField(widget=forms.TextInput(attrs={'class': 'geo', 'readonly': 'readonly'}), required=False, initial='',)
    lat_s = forms.CharField(widget=forms.TextInput(attrs={'class': 'geo', 'readonly': 'readonly'}), required=False, initial='',)
    lon_w = forms.CharField(widget=forms.TextInput(attrs={'class': 'geo', 'readonly': 'readonly'}), required=False, initial='',)
    lon_e = forms.CharField(widget=forms.TextInput(attrs={'class': 'geo', 'readonly': 'readonly'}), required=False, initial='',)
    date  = forms.ChoiceField(choices=DATE_FROM, widget=forms.Select(), required=False, )

    start_date= forms.DateTimeField(widget=DateTimePickerInput(attrs={'class': 'datetime', }), required=False )
    end_date = forms.DateTimeField(widget=DateTimePickerInput(attrs={'class': 'datetime', }), required=False)

