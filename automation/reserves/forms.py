#
# encoding: utf-8
#
from django.utils.translation import gettext_lazy as _
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout #, Row, Column
from .models import (Stock, Product, Packaging, Location, ProductType)


def years_choice():
    choices=[('', _('All'))]
    for stock in Stock.objects.filter(stocked=True).all():
        year = stock.created.year
        choice = (str(year), year)
        if choice not in choices:
            choices.append(choice)
    return choices


class StockFilterForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].empty_label = _("All")
        self.fields['packaging'].empty_label = _("All")   
        
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True).order_by('name').all(),
        widget=forms.Select(attrs={'class': 'w3-select', 'onChange': 'this.form.submit()'}),
        label=_("Product"),
        empty_label=_("All"),
        required=False,
    )

    product_type = forms.ModelChoiceField(
        queryset=ProductType.objects.order_by('name').all(),
        widget=forms.Select(attrs={'class': 'w3-select', 'onChange': 'this.form.submit()'}),
        label=_("Type"),
        empty_label=_("All"),
        required=False,
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(active=True).order_by('name').all(),
        widget=forms.RadioSelect(attrs={'class': 'w3-radio', 'onChange': 'this.form.submit()'}),
        label=_("Location"),
        required=False,
    )

    packaging = forms.ModelChoiceField(
        queryset=Packaging.objects.filter(active=True).order_by('name').all(),
        widget=forms.RadioSelect(attrs={'class': 'w3-radio', 'onChange': 'this.form.submit()'}),
        label=_("Packaging"),
        required=False,
    )

    alert = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'w3-check', 'onClick': 'this.form.submit()'}),
        label=_("Alert product"),
        required=False,
        initial=False,
    )

    removed = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'w3-check', 'onClick': 'this.form.submit()'}),
        label=_("Removed product"),
        required=False,
        initial=False,
    )

    expired = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'w3-check', 'onClick': 'this.form.submit()'}),
        label=_("Expired product"),
        required=False,
        initial=False,
    )
    
    to_order = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'w3-check', 'onClick': 'this.form.submit()'}),
        label=_("Product to order"),
        required=False,
        initial=False,
    )
    
    year = forms.ChoiceField(
        choices=years_choice,
        widget=forms.RadioSelect(attrs={'class': 'w3-radio', 'onChange': 'this.form.submit()'}),
        label=_("Years"),
        required=False,
    )

    class Meta:
        model = Stock
        fields = [
            'year', 'product', 'product_type', 'location', 'packaging', 'alert' , 'removed', 'expired',  
        ]
        
        
class DateInput(forms.DateInput):
    input_type = 'date'


class StockEditForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init()
    
    def init(self):
        self.initial['created'] = self.instance.created.isoformat()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'created',
            'location',
            'range',
            'packaging',
            'expiry_date_days',
            'amount'
        )        
        
        
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(active=True).order_by('name').all(),
        widget=forms.RadioSelect(attrs={'class': 'w3-radio'}),
        label=_("Location"),
        required=True,
    )

    packaging = forms.ModelChoiceField(
        queryset=Packaging.objects.filter(active=True).order_by('name').all(),
        widget=forms.RadioSelect(attrs={'class': 'w3-radio', }),
        label=_("Packaging"),
        required=True,
    )

    class Meta:
        model = Stock
        fields = [
            'created', 'location', 'packaging', 'expiry_date_days', 'range', 'amount', 
        ]
        widgets = {
            'created': DateInput(attrs={'class': 'w3-input'}),      
            'expiry_date_days': forms.NumberInput(attrs={'min': 30, 'max': 800}),
            'range': forms.NumberInput(attrs={'min': 1, 'max': '10'}),
            'amount': forms.NumberInput(attrs={'min': 1, 'max': '100'}),
        }
        
class StockCreateForm(StockEditForm):
         
    def init(self):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'created',
            'product',
            'location',
            'range',
            'packaging',
            'expiry_date_days',
            'amount'
        )         
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(active=True).order_by('name').all(),
        widget=forms.Select(attrs={'class': 'w3-select', }),
        label=_("Product"),
        required=True,
    )

    class Meta:
        model = Stock
        fields = [
            'created', 'product', 'location', 'packaging', 'expiry_date_days', 'range', 'amount', 
        ]
        widgets = {
            'created': DateInput(attrs={'class': 'w3-input'}), 
            'expiry_date_days': forms.NumberInput(attrs={'min': 30, 'max': '700'}),
            'range': forms.NumberInput(attrs={'min': 1, 'max': '20'}),
            'amount': forms.NumberInput(attrs={'min': 1, 'max': '1000'}),
        }
      
        