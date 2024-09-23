#
# encoding: utf-8
import threading
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect#, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from contrib.views import Render
from automation.tasks import send_mail
from .models import Stock
from .filters import stockFilter
from .forms import StockFilterForm, StockCreateForm, StockEditForm


@login_required
@csrf_exempt
def stock_remove(request, pk=None):
    if request.method == "POST":
        if pk:
            stock = Stock.objects.filter(pk=pk)
            amount = stock[0].amount - 1
            if amount <= 0:
                amount = 0
                stock.update(stocked=False, amount=0)
            else:
                stock.update(amount=amount)
            return JsonResponse({'status': True, 'amount': amount})

    return JsonResponse({'status': False})


@login_required
@csrf_exempt
def stock_add(request, pk=None, new=None):
    if request.method == "POST":
        if pk:
            stock = Stock.objects.filter(pk=pk)
            amount = stock[0].amount + 1
            if amount <= 1:
                amount = 1
                stock.update(created=timezone.now(), amount=amount, stocked=True)
            else:
                stock.update(amount=amount)
            return JsonResponse({'status': True, 'amount': amount})
    return JsonResponse({'status': False})



def _pdf_mail_to(request, file_path, content):
    with open(file_path, 'wb') as f:
        f.write(content)
    send_mail(str(_('Order list')), str(_('Order pdf attached')), to=[request.user.email], attachments=[file_path])
        
        
def pdf_mail_to(request, file_path, content):
    threading.Thread(target=_pdf_mail_to, args=[request, file_path, content, ], daemon=True).start()        
        
        
@login_required
def order_to_pdf(request):
    try:
        queryset, title = stockFilter(request)
        datas = dict(
            pagesize='A4',
            request=request,
            title=title,
            recs=queryset
        )
        filename=str(_('order-list'))     
        return Render.render(request, 'reserves/order-print.html', datas, filename=filename, cb=pdf_mail_to)   
    except Exception as e:
        print(f"order_to_pdf error: {e}")
    return HttpResponseRedirect(reverse('reserves:stock_list'))


class StockList(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'reserves/stock-list.html'
    context_object_name = 'qs'

    def get_queryset(self):
        qs, _ = stockFilter(self.request)
        return qs

    def get_context_data(self, **kwargs):  
        context = super().get_context_data(**kwargs)
        context['form'] = StockFilterForm(data=self.request.GET or None)
        return context
    

class StockCreate(LoginRequiredMixin,CreateView):
    model = Stock
    template_name = 'reserves/product-add.html'
    form_class = StockCreateForm
    success_url = reverse_lazy('reserves:stock_create')


class StockEdit(LoginRequiredMixin, UpdateView):
    model = Stock
    template_name = 'reserves/product-edit.html'
    form_class = StockEditForm
    success_url = reverse_lazy('reserves:stock_list')
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock'] = Stock.objects.get(pk=self.kwargs.get('pk'))
        return context

