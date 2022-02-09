import json

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.pos.forms import *
from core.security.mixins import PermissionMixin


class ProductStartListView(PermissionMixin, ListView):
    model = ProductStart
    template_name = 'scm/productStart/list.html'
    permission_required = 'view_productstart'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('productStart_create')
        context['title'] = 'Listado de Productos Start'
        return context


class ProductStartCreateView(PermissionMixin, CreateView):
    model = ProductStart
    template_name = 'scm/productStart/create.html'
    form_class = ProductStartForm
    success_url = reverse_lazy('productStart_list')
    permission_required = 'add_productstart'

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'product':
                if ProductStart.objects.filter(product_id=obj):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                data = self.get_form().save()
            elif action == 'validate_data':
                return self.validate_data()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un Producto Start'
        context['action'] = 'add'
        return context


class ProductStartUpdateView(PermissionMixin, UpdateView):
    model = ProductStart
    template_name = 'scm/productStart/create.html'
    form_class = ProductStartForm
    success_url = reverse_lazy('productStart_list')
    permission_required = 'change_productstart'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            id = self.get_object().id
            if type == 'name':
                if Category.objects.filter(product_id=obj).exclude(id=id):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'edit':
                data = self.get_form().save()
            elif action == 'validate_data':
                return self.validate_data()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de un Producto Start'
        context['action'] = 'edit'
        return context


class ProductStartDeleteView(PermissionMixin, DeleteView):
    model = ProductStart
    template_name = 'scm/productStart/delete.html'
    success_url = reverse_lazy('productStart_list')
    permission_required = 'delete_productstart'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
