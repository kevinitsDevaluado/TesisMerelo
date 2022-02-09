import json

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse,HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages

from core.security.mixins import PermissionMixin
from core.pos.forms import Sale, SaleDetail

def order_pending_list(request):
    model = Sale, SaleDetail
    template_name = 'scm/order/list.html'
    context = {
        "object_list": Sale.objects.filter(estado=True, disponibilidad=0),
        "object_list2": SaleDetail.objects.all(),
        "title": 'Listado de Pedidos recientes',
        "disponibilidad": '0'
    }

    return render(request, template_name, context)

def order_accepted_list(request):
    model = Sale
    template_name = 'scm/order/list.html'

    context = {
        "object_list": Sale.objects.filter(estado=True, disponibilidad=1),
        "title": 'Listado de Pedidos aceptados',
        "disponibilidad": '1'
    }

    return render(request, template_name, context)

def order_rejected_list(request):
    model = Sale
    template_name = 'scm/order/list.html'

    context = {
        "object_list": Sale.objects.filter(estado=True, disponibilidad=2),
        "title": 'Listado de Pedidos rechazados',
        "disponibilidad": '2'
    }

    return render(request, template_name, context)

def update_order(request,id):
    disponibilidad = request.POST.get('disponibilidad')
    sale = Sale.objects.filter(id=id,estado=True).first()

    sale.disponibilidad = disponibilidad
    sale.save()

    messages.success(request, "Estado del pedido actualizado")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

