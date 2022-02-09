from django.urls import path

from core.shoppingcard.views import *

urlpatterns = [
    path('', ShoppingCardIndexView, name='shopping_index'),
    path('shopping/search/<int:id>/', buscar_categorias , name='buscar_categoria'),
    path('shopping/search', search , name='search_products'),
    path('shopping/update_item', update_item , name='update_item'),
    path('shopping/detail/<slug>', detail , name='detail'),
    path('shopping/cart', cart , name='cart'),
    path('shopping/simple_checkout', simple_checkout , name='simple_checkout'),
    path('shopping/verify_sale', verify_sale , name='verify_sale'),
    path('shopping/mis_pedidos', mis_pedidos , name='mis_pedidos'),
    path('shopping/registrarte', registro , name='registrarte'),

]
