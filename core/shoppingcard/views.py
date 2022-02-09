from datetime import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import TemplateView,FormView,CreateView

from core.pos.models import Product, Sale, Client, Provider, Category, Purchase, Company
from core.reports.choices import months
from core.security.models import Dashboard
from django.contrib import messages
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.pos.models import *
from core.user.forms import UserForm, ProfileForm
from django.urls import reverse_lazy
from .forms import *
from core.security.models import *
from core.pos.forms import Sale, SaleDetail


from django.views.decorators.csrf import csrf_protect

from django.http import HttpResponse, JsonResponse

# Create your views here.
def ShoppingCardIndexView(request):
    template_name = 'shopping/index.html'

    if request.user.is_authenticated:
        client = request.user.client
        sale, created = Sale.objects.get_or_create(
            client=client, estado=False)
        items = sale.saledetail_set.all().order_by('id')
        cartItems = sale.get_cart_items
    else:
        items = []
        sale = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0
    
    context = {
         "products":Product.objects.all(),
         "descc":PromotionsDetail.objects.all(),
         "company":Company.objects.first(),
         "productodelmes":ProductStart.objects.first(),
         "categorias":Category.objects.filter(activo=True),
         "productoM": ProductStart.objects.filter(activo=True),
         "items": items,
         "cartItems": cartItems,
         "sale":sale
    }
    return render(request,template_name,context) 

#199080

def registro(request):
    template_name = "shopping/registrarte.html"
    
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            name = request.POST['first_name']
            print("Nombre ingresado: ",name)
            apellidos = request.POST['last_name']
            direccion = request.POST['direccion']
            telefono = request.POST['telefono']

            print("Apellido ingresado: ",apellidos)
            cedula = request.POST['dni']
            print("Cedula ingresada: ",cedula)
            u = User()
            u.first_name = apellidos
            u.last_name = name
            u.username = cedula
            u.dni = cedula
            u.set_password(cedula)
            u.save()
            cliente = Client()
            cliente.user = u
            cliente.address = direccion
            cliente.mobile = telefono
            cliente.save()
            group = Group.objects.get(name="Cliente")
            u.groups.add(group)
            messages.success(request, 'Usuario Creado con Exito.! El usuario y contraseña es su DNI')

        #email = request.POST['email']
        #print("Email ingresada: ",email)
    else:
        
        form = UsuarioForm()
    company = Company.objects.first()
    productoM = ProductStart.objects.filter(activo=True)
    categorias = Category.objects.filter(activo=True)
    context = {"categorias":categorias,"company":company,"productoM":productoM,"form":form}
    return render(request, template_name, context)

def buscar_categorias(request,id):
    template_name = "shopping/list_product.html"
    # cat = Category.objects.get(slug=slug)
    if request.user.is_authenticated:
        client = request.user.client
        sale, created = Sale.objects.get_or_create(
            client=client, estado=False)
        items = sale.saledetail_set.all().order_by('id')
        cartItems = sale.get_cart_items
    else:
        items = []
        sale = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0

    company = Company.objects.first()
    productoM = ProductStart.objects.filter(activo=True)

    promotions = PromotionsDetail.objects.all()
    categorias = Category.objects.filter(id=id,activo=True)
    productos = Product.objects.filter(activo=True,category_id=id)
    context = {"productos":productos,"categorias":categorias,"company":company,"productoM":productoM,"items": items,"cartItems": cartItems,"sale":sale,"promociones":promotions}
    return render(request,template_name,context) 


def detail(request,slug):
    if Product.objects.filter(activo=True,slug=slug).exists():
        template_name = "shopping/details.html"
        producto = Product.objects.get(activo=True,slug=slug)
        categorias = Category.objects.filter(activo=True)
        context = {"producto":producto,"categorias":categorias}
        return render(request,template_name,context)

def cart(request): 
    template_name = "shopping/cart.html"
    
    if request.user.is_authenticated:
        client = request.user.client
        sale, created = Sale.objects.get_or_create(
            client=client, estado=False)
        items = sale.saledetail_set.all().order_by('id')
        cartItems = sale.get_cart_items
    else:
        items = []
        sale = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0

    context = {
         "items": items,
         "cartItems": cartItems,
         "sale":sale
    }
    return render(request, template_name, context)

def search(request):
    template_name = "shopping/list_product.html"
    q = request.GET['q']    
    productos = Product.objects.filter(activo=True,name__icontains=q)
    categorias = Category.objects.filter(activo=True)
    promotions = PromotionsDetail.objects.all()
    company = Company.objects.first()
    if request.user.is_authenticated:
        client = request.user.client
        sale, created = Sale.objects.get_or_create(
            client=client, estado=False)
        items = sale.saledetail_set.all().order_by('id')
        cartItems = sale.get_cart_items
    else:
        items = []
        sale = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0
    for i in productos:
        print('Productos',i.name)
    context = {"productos":productos,"categorias":categorias,"promociones":promotions,"company":company,
    "items": items,
         "cartItems": cartItems,
         "sale":sale
    }
    return render(request,template_name,context)

def update_item(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']

        client = request.user.client
        product = Product.objects.get(id=productId)
        sale, created = Sale.objects.get_or_create(client=client, estado=False)
        saledetail, created = SaleDetail.objects.get_or_create(
                sale=sale, product=product)
            
        if action == 'add':

            verify_product = SaleDetail.objects.filter(sale=sale.id,product=productId).first()
            if verify_product:
                product = Product.objects.filter(id=productId,activo=True).first()
                if product:
                    if product.stock > verify_product.cant:
                        saledetail.cant = (saledetail.cant + 1)
                        messages.success(request, "Producto agregado al carrito")
                    else:
                        messages.success(request, "Lo sentimos no disponemos de esa cantidad de productos")
                       

                else:
                    messages.success(request, "Ah ocurrido un error intentelo más tarde")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.success(request, "Ah ocurrido un error intentelo más tarde")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        elif action == 'remove':
            saledetail.cant = (saledetail.cant - 1)
        
        saledetail.save()

        if saledetail.cant <=0:
            saledetail.delete()
        
        return JsonResponse("Agregado", safe=False)

    return JsonResponse("Hola guapo", safe=False)

def simple_checkout(request):
    template_name = "shopping/simple_checkout.html"

    if request.user.is_authenticated:
        client = request.user.client
        sale, created = Sale.objects.get_or_create(
            client=client, estado=False)
        items = sale.saledetail_set.all().order_by('id')
        cartItems = sale.get_cart_items
    else:
        items = []
        sale = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0

    context = {
         "items": items,
         "cartItems": cartItems,
         "sale":sale,
         "company":Company.objects.first(),
    }
    return render(request, template_name, context)

def verify_sale(request):
    template_name = 'shopping/index.html'
    
    if request.user.is_authenticated:

        total = request.POST.get('total')
        comp = Company.objects.first()
        
        client = request.user.client
        sale, created = Sale.objects.get_or_create(
            client=client, estado=False)
            
        items = sale.saledetail_set.all().order_by('id')
        cartItems = sale.get_cart_items

        sale_products = SaleDetail.objects.filter(sale=sale.id)
        for product in sale_products:
            productos = Product.objects.filter(id=product.product.id,activo=True).first()
            if productos:
                productos.stock = productos.stock - product.cant
                productos.save()
            else:
                messages.success(request, "Ah ocurrido un error intentelo más tarde")
                return redirect("shopping_index")

        sale.estado = True
        sale.image = request.FILES.get('imageSale')
        sale.subtotal = sale.get_cart_total
        sale.iva = comp.iva
        sale.total_iva =  format(sale.get_cart_total * (comp.iva/100), '.2f')
        total_finish = (sale.get_cart_total * (comp.iva/100)) + sale.get_cart_total
        sale.total = format(total_finish, '.2f')
        sale.cash = format(total_finish, '.2f')
        sale.save()

        if sale.estado == True:
            messages.success(request, "Pedido relizado correctamente")
            return redirect("shopping_index")
        else:
            messages.success(request, "Lo sentimos a ocurrido un error intentelo más tarde")
            return redirect("shopping_index")


    else:
        items = []
        sale = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0

    context = {
         "items": items,
         "cartItems": cartItems,
         "sale":sale
    }

    return render(request, template_name, context)

def mis_pedidos(request): 
    template_name = "shopping/mis_pedidos.html"
    model = Sale, SaleDetail
    if request.user.is_authenticated:
        client = request.user.client
        sale, created = Sale.objects.get_or_create(
            client=client, estado=False)
        items = sale.saledetail_set.all().order_by('id')
        cartItems = sale.get_cart_items

        order = Sale.objects.filter(client_id=request.user.client.id, estado=True)

    else:
        items = []
        sale = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0
        order = []

    context = {
         "items": items,
         "cartItems": cartItems,
         "sale":sale,
         "order":order,
         "object_list": Sale.objects.filter(estado=True, disponibilidad=0),
         "object_list2": SaleDetail.objects.all(),
         "company":Company.objects.first(),


    }
    return render(request, template_name, context)


def mycart(request):
    template_name = "shopping/cart.html"
    sess = request.session.get("data",{"items":[]})
    products = Product.objects.filter(activo=True,slug__in=sess["items"])
    categorias = Category.objects.filter(activo=True)
    context = {"productos":products,"categorias":categorias}
    return render(request, template_name, context)




class ClienteCreateView(CreateView):
    model = User
    template_name = 'shopping/registrarte.html'
    form_class = UserForm
    success_url = reverse_lazy('user_list')
    permission_required = 'add_user'

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'cedula':
                if User.objects.filter(dni=obj):
                    data['valid'] = False
            elif type == 'username':
                if User.objects.filter(username__icontains=obj):
                    data['valid'] = False
            elif type == 'email':
                if User.objects.filter(email=obj):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST['action']
        try:
            if action == 'add':
                nombres = request.POST['nombres']
                apellidos = request.POST['apellidos']
                cedula = request.POST['cedula']
                email = request.POST['email']
                print('NOmbres: ', nombres)
                print('apellidos: ',apellidos)
                print('cedula: ',cedula)
                print('email: ', email)

                
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
        context['title'] = 'Nuevo registro de un Usuario'
        context['action'] = 'add'
        context['products'] = Product.objects.all()
        context['company'] = Company.objects.first()
        context['productodelmes'] = ProductStart.objects.first()
        context['categorias'] = Category.objects.filter(activo=True)   
        context['productoM'] = ProductStart.objects.filter(activo=True)
        return context








