# Create your models here.
import pathlib, json
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django_resized import ResizedImageField
from django.db import models
from django_celery_beat.models import PeriodicTask
from colorfield.fields import ColorField
#import paho.mqtt.publish as publish
from automation.models import SensorGroup, Location
from contrib import utils
from .forms import DATE_RANGE, FREQ_CHOICES, REFRESH_CHOICES, LINE_MODES, INTERPOLATIONS

class Unit(models.Model):
    name = models.CharField(_("Measurement unit"), max_length=64, null=True)
    unit = models.CharField(_("Unit"), unique=True, max_length=8, null=True, blank=True)

    class Meta:
        ordering = ['unit']
        verbose_name = _("Units")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.unit}'


class Plot(models.Model):
    title  = models.CharField(_("Title"), help_text=_("Plot title"), max_length=100, null=True, blank=True)
    xtitle = models.CharField(_("X title"), help_text=_("Title for x axe"), max_length=100, null=True, blank=True)

    figure = models.CharField(_("Figure"), help_text=_("Default figure data name (in mqtt message)"), max_length=8, null=True, blank=True)
    frequency = models.CharField(_("Frequency"), choices=FREQ_CHOICES, help_text=_("Default frequency is seconds"), max_length=10, null=True, blank=True, default='15s')
    refresh = models.IntegerField(_("Refreshment"), choices=REFRESH_CHOICES, help_text=_("Default refreshment in seconds"), null=True, blank=True, default=30)
    date_range = models.CharField(_("Date range"), choices=DATE_RANGE, help_text=_("Default since date range"), max_length=10, null=True, blank=True, default='-30m')
    mode = models.CharField(_("Line"), choices=LINE_MODES, help_text=_("Default line modes"), max_length=24, null=True, blank=True, default='lines')
    interpolation = models.CharField(_("Interpolation"), choices=INTERPOLATIONS, max_length=16, help_text=_("Default Interpolation mode"), null=True, blank=True, default='spline')
    slider = models.BooleanField(_("Slider"), help_text=_("Plotly slider view for plot"), default=False)
    range_selector = models.BooleanField(_("Range selector"), help_text=_("Plotly display range selector bar"), default=False)
    active = models.BooleanField(_("Active"), default=True)
    
    @property
    def plotParams(self):
        return {
            'title': self.title,
            'xtitle': self.xtitle,
            'slider': self.slider,
            'frequency': self.frequency,
            'refresh': self.refresh,
            'range_selector': self.range_selector,
        }

    class Meta:
        ordering = ['title']
        verbose_name = _("Plot")
        verbose_name_plural =  _("Plots")

    def __str__(self):
        return f'{self.title}'


class Fields(models.Model):
    FUNCS = [
        (None, _("No Aggregation")),
        ("mean", _("Mean")),
        ("median", _("Median")),
        ("max", _("Max")),
        ("min", _("Min")),
        ("sum", _("Sum")),
        ("count", _("Count")),
    ]
    
    plot = models.ForeignKey(Plot, verbose_name=_("Data type and description"), on_delete=models.CASCADE, null=True, blank=True, )
    label = models.CharField(_("Data label"), help_text=_("Data label for plot"), max_length=100, null=True, blank=True)
    name  = models.CharField(_("Data name"), help_text=_("Data name in mqtt message"), max_length=8, null=True, blank=True)
    unit  = models.ForeignKey(Unit, verbose_name=_("Unit"), on_delete=models.CASCADE, null=True, blank=True)
    
    metric = models.BooleanField(_("Metric"), help_text=_("Is data metric for plot"), default=False)
    func = models.CharField(_("Function"), choices=FUNCS, help_text=_("Function to apply"), max_length=16, default='Avg')
    color = ColorField(_("Chart"), help_text=_("Chart color for plot"), blank=True, null=True, default='#8BFFBE')
    note_color = ColorField(_("Annotation"), help_text=_("Annotation color for plot"), blank=True, null=True, default='#FF00FF')
    connect_gaps= models.BooleanField(_("Gaps"), help_text=_("Connect gaps for plot"), null=True, blank=True, default=False)
    
    
    @property
    def plot_field(self):
        return [self.name, self.label, self.unit, self.color, self.note_color, self.connect_gaps]
     
     
    def aggregate(self, v): 
        if self.func is not None:
            return self.func(v)
        return None
          
        
    class Meta:
        ordering = ['name']
        unique_together = ["plot", "name"]
        verbose_name = _("Field for plot")
        verbose_name_plural = _("Fields for plot")


    def __str__(self):
        return f'{self.plot.title}'


class Device(models.Model):
    RECORD_NONE = 0
    RECORD_CONTINUOUS = 1
    RECORD_MOTION_DETECTION = 2
    
    RECORD_TYPE = [
        (RECORD_NONE, _("No")),
        (RECORD_CONTINUOUS, _("Continuous")),
        (RECORD_MOTION_DETECTION, _("Detection for video")),
    ]   
        
    name = models.CharField(_("Device name"), max_length=128, blank=False, null=True)
    sensor = models.SlugField(_("Sensor name"), help_text=_("Influxdb bucket and mqtt sensor (Unique max 64 chars long)"), max_length=64, null=True, blank=False, )
    vendor = models.CharField(_("Vendor name"), max_length=64, blank=True, null=True)
    model_id = models.CharField(_("Device model id"), max_length=128, blank=True, null=True)
    description = models.CharField(_("Device description"), max_length=128, null=True, blank=True)
    group = models.ForeignKey(SensorGroup, verbose_name=_("Sensor group"), on_delete=models.CASCADE, null=True, blank=True, )
    location = models.ForeignKey(Location, verbose_name=_("Device location"), on_delete=models.CASCADE, null=True, blank=True, )
    ## mqtt elements
    org =  models.SlugField(_("Organisation"), help_text=_("MQTT origine and Influxdb Organisation"), max_length=64, blank=False, null=True, default="home")
    uuid = models.SlugField(_("Device uuid"), help_text=_('Unique id device'), unique=True, max_length=32, null=True, blank=True)
    datas = models.TextField(_("Data format"), help_text=_("MQTT data description in json format"), null=True, blank=True, default='{}')
    options = models.TextField(_("Data option"), help_text=_("MQTT option description in json format"), null=True, blank=True, default='{}')
    basetopic = models.CharField(_("Base topic"), max_length=128, null=True, blank=True, default="home")
    ## Service if exists
    ip = models.CharField(_("Device IP or network address"), max_length=32, null=True, blank=True)
    service = models.CharField(_("Supervisor service"), max_length=64, null=True, blank=True)
    ## Record and Database
    items = models.TextField(_("Data name"), help_text=_("List of data name to record in json format"), null=True, blank=True, default='[]')
    tags = models.TextField(_("Influxdb tags"), help_text=_("Influxdb tags list in json format"), null=True, blank=True, default='{}')
    plot = models.ForeignKey(Plot, verbose_name=_("Data and description for plot"), on_delete=models.CASCADE, null=True, blank=True, )
    record = models.PositiveSmallIntegerField(_("Record"), choices=RECORD_TYPE, help_text=_("Database recording mode"), default=0)
    ## Dashboard elements
    image = ResizedImageField(_("Device image"), size=[320, 240], upload_to='devices/', null=True, blank=True, default = 'devices/no-image.png')
    display = models.BooleanField(_("Display device"), help_text=_("Display device in dashboard"), default=True)
    bg = models.CharField(_("Default background"), max_length=128, null=True, blank=True, default="w3-dark-light")
    width = models.IntegerField(_("Minimum width (px)"), default=320)
    height = models.IntegerField(_("Minimum height (px)"), default=250)
    ## Active or not
    active = models.BooleanField(_("Active"), default=True)


    @property
    def get_items(self):
        return json.loads(self.items)
    
    
    @property
    def get_datas(self):
        return json.loads(self.datas)
    
    
    @property
    def get_options(self):
        return json.loads(self.options)       
        
        
    def image_tag(self):
        return mark_safe(f'<img src="{self.image.url}" style="height:32px;">')
    image_tag.short_description = _("Device image")
    image_tag.allow_tags = True


    def set_js_template(self, name, js):
        filename = settings.DEVICES_TEMPLATES_ROOT / f'{name}' / f'{js}.html'

        if not pathlib.Path(filename).is_file():
            with open(filename, 'w') as f:
                f.writelines([
                    "    <script>\n",
                    "        function " + f"{name}" +"Control(mqtt, args, payload) {}\n",
                    "    </script>\n",
                ])


    def set_model_template(self, model='box', js='js'):
        name = f'{self.sensor}'
        folder = settings.DEVICES_TEMPLATES_ROOT / f'{name}'
        folder.mkdir(parents=True, exist_ok=True)

        filename = folder / f'{model}.html'
        if not pathlib.Path(filename).is_file():
            with open(filename, 'w') as f:
                f.writelines([
                    "{% extends " + f'\"devices/device-{model}.html\"' + " %}\n",
                    "{% load i18n boardtags %}\n",
                    "{% block " + f"{model}_detail" +" %}\n{% include " + f'\"devices/{name}/{js}.html\"' + " %}\n{% endblock %}\n",
                ])
                self.set_js_template(name, js)


    class Meta:
        ordering = ['name']
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
       
    
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = utils.get_device_uuid()
        self.uuid = slugify(self.uuid)
        self.org = slugify(self.org)
        self.sensor = self.sensor.replace('-', '_')
        self.basetopic = f'{self.org}/{self.uuid}'
        super().save(*args, **kwargs)


    def subscriptions(self):
        subs = []
        for top in TopicSubscription.objects.filter(device_id=self.id).all():
            subs.append([top.subs, 0])
        return subs


    def __str__(self):
        return f'{self.uuid}: {self.name}'


class DeviceLinked(models.Model):
    device = models.ForeignKey(Device, verbose_name=_("Master device"), related_name='master', on_delete=models.CASCADE, null=True, blank=True)
    link = models.ForeignKey(Device, verbose_name=_("Linked device to master device"), related_name='linked', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['device__name']
        verbose_name = _("Linked device")
        verbose_name_plural = _("Linked devices")
        
    def __str__(self):
        return f'{self.device.name}<<{self.link.name}'        


class TopicSubscription(models.Model):
    device = models.ForeignKey(Device, verbose_name=_("Device"), on_delete=models.CASCADE, null=True, blank=True, )
    subs = models.CharField(_("Subscription"), max_length=128, blank=False, null=True, default="#")

    class Meta:
        ordering = ['subs']
        verbose_name = _("Topic subscription")
        verbose_name_plural = _("Topics subscription")

    def __str__(self):
        return f'{self.subs}'


class PeriodicTaskDevice(models.Model):
    task = models.ForeignKey(
        PeriodicTask,
        verbose_name=_("Periodic task"),
        help_text=_("Select an exixting task"),
        on_delete=models.RESTRICT, null=True, blank=False
    )
    device = models.ForeignKey(
        Device,
        verbose_name=_("Device"),
        on_delete=models.RESTRICT,
        null=True,
        blank=True
    )
    class Meta:
        ordering = ['device__name']
        verbose_name = _("Periodic task per device")
        verbose_name_plural = _("Periodics tasks per device")

  
class DeviceProcessing(models.Model):
    device = models.ForeignKey(Device, verbose_name=_("Device"), on_delete=models.CASCADE, null=True, blank=False)
    description = models.CharField(_("Short description"), max_length=100, null=True, blank=True)
    class_module = models.CharField(_("Module class"), help_text=_("Python module class"), max_length=128, null=True, blank=False, default='devices.modules.processing.Base')
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ['device__name']
        verbose_name = _("Device processing module")
        verbose_name_plural = _("Devices processing module")

    def __str__(self):
        return f'{self.device.name}'


