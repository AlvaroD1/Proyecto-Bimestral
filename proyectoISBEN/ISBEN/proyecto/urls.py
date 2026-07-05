from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login-role/', views.login_role, name='login_role'),
    path('logout-role/', views.logout_role, name='logout_role'),
    
    # Dashboards
    path('dashboard/proveedor/', views.dashboard_proveedor, name='dashboard_proveedor'),
    path('dashboard/vendedor/', views.dashboard_vendedor, name='dashboard_vendedor'),
    path('dashboard/comprador/', views.dashboard_comprador, name='dashboard_comprador'),
    
    # Registros de perfiles
    path('proveedor/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('vendedor/crear/', views.crear_vendedor, name='crear_vendedor'),
    path('comprador/crear/', views.crear_comprador, name='crear_comprador'),
    
    # CRUD Productos
    path('producto/crear/', views.crear_producto, name='crear_producto'),
    path('producto/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    
    # Pedidos
    path('producto/comprar/<int:id>/', views.comprar_producto, name='comprar_producto'),
    path('pedido/enviar/<int:id>/', views.enviar_pedido, name='enviar_pedido'),
    path('pedido/recibir/<int:id>/', views.recibir_pedido, name='recibir_pedido'),
]
