# encoding: utf-8
#
#from datetime import timedelta
#from dateutil.relativedelta import relativedelta
#from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django import forms
#from devices.models import Fields 

FREQ_CHOICES = [
    ('5s', _('5 seconds')),
    ('10s', _('10 seconds')),
    ('15s', _('15 seconds')),
    ('30s', _('30 seconds')),
    ('1m', _('1 minute')),
    ('5m', _('5 minutes')),    
    ('15m', _('15 minutes')),    
    ('30m', _('30 minutes')),
    ('1h', _('1 hour')),    
    ('3h', _('3 hours')),     
    ('6h', _('6 hours')),     
    ('12h', _('12 hours')),
    ('24h', _('24 hours')), 
    ('1d', _('1 day')), 
]

REFRESH_CHOICES = (
    (5, _("5 s")),
    (10, _("10 s")),
    (15, _("15 s")),
    (30, _("30 s")),
    (60, _("1 mn")),
    (120, _("2 mn")),
    (300, _("5 mn")),
    (600, _("10 mn")),
    (1800, _("30 mn")),
)

DATE_RANGE= [
    ('-1m', _('Since 1 minute')),
    ('-5m', _('Since 5 minutes')),
    ('-10m', _('Since 10 minutes')),
    ('-15m', _('Since 15 minutes')),
    ('-30m', _('Since 30 minutes')),
    ('-1h', _('Since 1 hour')),
    ('-3h', _('Since 3 hours')),
    ('-6h', _('Since 6 hours')),
    ('-12h', _('Since 12 hours')),
    ('-24h', _('Since 24 hours')),
    ('-2d', _('Since 2 days')),
    ('-3d', _('Since 3 days')),
    ('-4d', _('Since 4 days')),
    ('-5d', _('Since 5 days')),
    ('-6d', _('Since 6 days')),
    ('-7d', _('Since a week')),
    ('-14d', _('Since 2 weeks')),
    ('-30d', _('Since 1 month')),
]

LINE_MODES = [
    ('lines', _('Lines')),
    ('markers', _('Markers')),
    ('lines+markers', _('Lines + markers')),
]

INTERPOLATIONS = [
    ('linear', _('Linear')),
    ('spline', _('Smooth line')),
    ('vhv', _('V-H-V')),
    ('hvh', _('H-V-H')),
    ('vh', _('V-H')),
    ('hv', _('H-V')),
]

def figure_list(device):
    from devices.models import Fields 
    lst = []
    for f in Fields.objects.filter(plot__id=device.plot.id):
        name, label, _, _, _, _ = f.plot_field
        if name is not None:
            lst.append((name, f'{name} {label}'))
    return lst


def PlotForm(device):
    attrs1 = {'onchange': 'graphReload();' }
    attrs2 = {'onchange': 'plotInit()();' }
    
    class _PlotForm(forms.Form):
        @staticmethod
        def plotform_initial():
            return dict(
                date_range=device.plot.date_range, 
                figure=device.plot.figure, 
                frequency=device.plot.frequency, 
                mode=device.plot.mode, 
                interpolation=device.plot.interpolation, 
                refresh=device.plot.refresh
            )
            
        date_range = forms.ChoiceField(choices=DATE_RANGE, widget=forms.Select(attrs=attrs1), label= _('Interval'), required=False,)
        figure = forms.ChoiceField(choices=figure_list(device), widget=forms.Select(attrs=attrs1), label=_('Figure'), required=False)
        frequency = forms.ChoiceField(choices=FREQ_CHOICES,  widget=forms.Select(attrs=attrs1), label=_("Frequency"), required=False)
        
        mode = forms.ChoiceField(choices=LINE_MODES, widget=forms.Select(attrs=attrs2), label=_("Line mode"), initial='lines', required=False)
        interpolation = forms.ChoiceField(choices=INTERPOLATIONS, widget=forms.Select(attrs=attrs2), label=_("Interpolation"), required=False)
        refresh = forms.ChoiceField(choices=REFRESH_CHOICES, widget=forms.Select(attrs=attrs2), label= _('Refresh'), required=False)
    return _PlotForm

        