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

    # Entrega segura y pagos
    path('pedido/confirmar-entrega/<int:id>/', views.confirmar_entrega, name='confirmar_entrega'),
    path('pedido/completar-pago/<int:id>/', views.completar_pago, name='completar_pago'),

    # Postulaciones de Vendedores
    path('producto/postular/<int:id>/', views.postular_producto, name='postular_producto'),
    path('postulacion/aprobar/<int:id>/', views.aprobar_postulacion, name='aprobar_postulacion'),
    path('postulacion/rechazar/<int:id>/', views.rechazar_postulacion, name='rechazar_postulacion'),
    path('producto/solicitar-vendedor/<int:id>/', views.solicitar_vendedor, name='solicitar_vendedor'),

    # Alertas de stock y lista de reposición
    path('reposicion/agregar/<int:producto_id>/', views.agregar_a_reposicion, name='agregar_a_reposicion'),
    path('reposicion/lista/', views.ver_lista_reposicion, name='ver_lista_reposicion'),
    path('reposicion/eliminar/<int:item_id>/', views.eliminar_item_reposicion, name='eliminar_item_reposicion'),
    path('reposicion/enviar/<int:lista_id>/', views.enviar_lista_reposicion, name='enviar_lista_reposicion'),
    path('inventario/actualizar/<int:inventario_id>/', views.actualizar_inventario, name='actualizar_inventario'),

    # Descuentos por volumen
    path('descuento/agregar/<int:producto_id>/', views.agregar_descuento, name='agregar_descuento'),
    path('descuento/eliminar/<int:descuento_id>/', views.eliminar_descuento, name='eliminar_descuento'),

<<<<<<< HEAD
    # API Seguimiento GPS
    path('api/vendedor/actualizar-ubicacion/', views.actualizar_ubicacion_vendedor, name='actualizar_ubicacion_vendedor'),
    path('api/pedido/obtener-ubicacion/<int:pedido_id>/', views.obtener_ubicacion_vendedor, name='obtener_ubicacion_vendedor'),
=======
    # Perfiles
    path('perfil/comprador/', views.perfil_comprador, name='perfil_comprador'),
    path('perfil/vendedor/', views.perfil_vendedor, name='perfil_vendedor'),
    path('perfil/proveedor/', views.perfil_proveedor, name='perfil_proveedor'),
>>>>>>> a8c57b0 (Perfiles para cada Rol)
]

