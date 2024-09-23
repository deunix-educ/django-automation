# encoding: utf-8
#from django.utils.translation import gettext_lazy as _
from django import template
from django.utils.html import format_html
#from django.urls import reverse
#from django.conf import settings
from automation.models import NavPane
from devices.models import PeriodicTaskDevice

register = template.Library()

@register.simple_tag(takes_context=True)
def load_js_script(context, jsfile):
    js_registry = context.get('js_registry')
    if jsfile in js_registry:
        return ""
    js_registry.append(jsfile)
    tpl = template.loader.get_template(jsfile)
    return tpl.render({
        'request': context['request'],
    })

@register.simple_tag(takes_context=True)
def case_control_function(context, uuid, sensor):
    switch_case = ''
    if sensor:
        switch_case = format_html(f"""case "{uuid}": {sensor}Control(mqtt, args, payload); break;""")
    return switch_case


@register.simple_tag
def get_tasks(device):
    tasks =  PeriodicTaskDevice.objects.filter(device_id=device.id).order_by('task').all()   
    return tasks


@register.simple_tag
def get_page(page):
    return NavPane.objects.get(page__exact=page)


@register.simple_tag
def nav_pane(item, pos=1):
    result = f"""
    <div class="w3-cell-row">
        <div class="icon w3-cell w3-cell-middle">
            <a href="{item.link}" class="w3-bar-item w3-btn w3-padding-small w3-xlarge" target="{item.target or ''}" {item.options or ''} title="{item.label}">{item.icon.html}</a>
        </div>
        <div class="label w3-cell w3-cell-middle w3-padding-small">
           <a href="{item.link}" class="w3-no-deco" target="{item.target or ''}" {item.options or ''}><span class="w3-large w3-wide">{item.title}</span></a>
        </div>
    </div>
    """
    return format_html(result)


@register.simple_tag
def button_play_pause(btn, status='pause', cls="w3-btn w3-padding-1", js="", org='', title=''):
    result = f'''
    <a id="btn-{btn}" class="{cls}" title="{title}" {js}><i class="fa-solid fa-toggle-off w3-text-amber fa-2x {btn}"></i></a>&nbsp;
    (<span class="state-{btn}">{status}</span>)
    '''
    return format_html(result)

@register.simple_tag
def button_start_stop(btn, status='off', cls="w3-btn w3-padding-1", js="", title=''):
    result = f'''
    <a id="btn-{btn}" class="{cls}" title="{title}" {js}><i class="fa-solid fa-toggle-off w3-text-amber fa-2x {btn}"></i></a> 
    (<span class="state-{btn}">{status}</span>)
    '''
    return format_html(result)

@register.simple_tag
def button_reset(btn, cls="w3-btn w3-padding-1", js="", title=''):
    result = f'''<a id="rst-{btn}" class="{cls}" title="{title}" {js}><i class="fa-solid fa-repeat w3-text-amber fa-2x"></i></a>'''
    return format_html(result)

@register.simple_tag
def button_left_start_stop(btn, js=""):
    return button_start_stop(btn+'-0', js=js)

@register.simple_tag
def button_right_start_stop(btn, js=""):
    return  button_start_stop(btn+'-1', js=js)


