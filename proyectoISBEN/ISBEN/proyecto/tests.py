from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import Proveedor, Vendedor, Comprador, Producto, Pedido

class ISBENTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_complete_flow_with_orders(self):
        # 1. Registrar Proveedor
        response = self.client.post(reverse('crear_proveedor'), {
            'nombre': 'Distribuidora Alpina',
            'ruc': '1792345677001',
            'direccion': 'Av. Amazonas 123',
            'usuario': 'alpina_prov',
            'contrasenia': 'Alpina123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Proveedor.objects.count(), 1)
        proveedor = Proveedor.objects.first()
        self.assertEqual(proveedor.nombre, 'Distribuidora Alpina')
        self.assertEqual(proveedor.usuario, 'alpina_prov')

        # 2. Registrar Vendedor
        response = self.client.post(reverse('crear_vendedor'), {
            'nombre': 'Juan Perez',
            'cedula': '1723456789',
            'telefono': '0999999999',
            'usuario': 'juan_vend',
            'contrasenia': 'Juan1234'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vendedor.objects.count(), 1)
        vendedor = Vendedor.objects.first()

        # 3. Registrar Comprador
        response = self.client.post(reverse('crear_comprador'), {
            'nombre': 'Tienda Don Bosco',
            'cedula': '1712345678',
            'direccion': 'Calle Loja y Sucre',
            'usuario': 'bosco_comp',
            'contrasenia': 'Bosco123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comprador.objects.count(), 1)
        comprador = Comprador.objects.first()

        # 4. Iniciar sesión como Proveedor
        response = self.client.post(reverse('login_role'), {
            'usuario': 'alpina_prov',
            'contrasenia': 'Alpina123'
        })
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session.get('role'), 'proveedor')
        self.assertEqual(session.get('role_id'), proveedor.id)

        # 5. Crear Producto como Proveedor
        response = self.client.post(reverse('crear_producto'), {
            'nombre': 'Leche Entera 1L',
            'descripcion': 'Leche pasteurizada premium',
            'cantidad': 100,
            'precio': '1.20',
            'proveedor': proveedor.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Producto.objects.count(), 1)
        producto = Producto.objects.first()
        
        # Verificar métodos del modelo Proveedor y Producto
        self.assertEqual(proveedor.obtener_cantidad_productos(), 1)
        self.assertIn(producto, proveedor.obtener_productos())
        self.assertTrue(producto.tiene_stock())

        # 6. Cerrar Sesión de Proveedor
        response = self.client.get(reverse('logout_role'))
        self.assertEqual(response.status_code, 302)

        # 7. Iniciar Sesión como Comprador
        response = self.client.post(reverse('login_role'), {
            'usuario': 'bosco_comp',
            'contrasenia': 'Bosco123'
        })
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session.get('role'), 'comprador')

        # 8. Comprar Producto (crea Pedido en estado Pendiente)
        response = self.client.post(reverse('comprar_producto', args=[producto.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verificar stock decrementado y pedido creado
        producto.refresh_from_db()
        self.assertEqual(producto.cantidad, 99)
        self.assertEqual(Pedido.objects.count(), 1)
        
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.estado, 'Pendiente')
        self.assertEqual(pedido.comprador, comprador)
        self.assertEqual(pedido.producto, producto)
        self.assertEqual(pedido.obtener_total(), Decimal('1.20'))
        
        # 9. Cerrar Sesión de Comprador
        response = self.client.get(reverse('logout_role'))
        self.assertEqual(response.status_code, 302)

        # 10. Iniciar sesión como Proveedor para despachar el pedido
        response = self.client.post(reverse('login_role'), {
            'usuario': 'alpina_prov',
            'contrasenia': 'Alpina123'
        })
        self.assertEqual(response.status_code, 302)
        
        # Enviar pedido
        response = self.client.post(reverse('enviar_pedido', args=[pedido.id]))
        self.assertEqual(response.status_code, 302)
        
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'Enviado')

        # 11. Cerrar Sesión
        response = self.client.get(reverse('logout_role'))
        self.assertEqual(response.status_code, 302)

        # 12. Iniciar sesión como Comprador para confirmar la recepción
        response = self.client.post(reverse('login_role'), {
            'usuario': 'bosco_comp',
            'contrasenia': 'Bosco123'
        })
        self.assertEqual(response.status_code, 302)
        
        # Recibir pedido
        response = self.client.post(reverse('recibir_pedido', args=[pedido.id]))
        self.assertEqual(response.status_code, 302)
        
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'Recibido')
        
        self.assertEqual(comprador.obtener_total_gastado(), Decimal('1.20'))

    def test_password_strength_validation(self):
        # Intentar registrar Proveedor con contraseña débil (sin números/mayúsculas)
        response = self.client.post(reverse('crear_proveedor'), {
            'nombre': 'Distribuidora Alpina',
            'ruc': '1792345677001',
            'direccion': 'Av. Amazonas 123',
            'usuario': 'alpina_bad',
            'contrasenia': 'password'
        })
        # Debe fallar la validación y recargar la página (código 200, no 302 redirect)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Proveedor.objects.filter(usuario='alpina_bad').count(), 0)

    def test_unique_username_across_roles(self):
        # Registrar un comprador con el usuario 'test_user'
        self.client.post(reverse('crear_comprador'), {
            'nombre': 'Tienda Don Bosco',
            'cedula': '1712345678',
            'direccion': 'Calle Loja y Sucre',
            'usuario': 'test_user',
            'contrasenia': 'Bosco123'
        })
        self.assertEqual(Comprador.objects.filter(usuario='test_user').count(), 1)

        # Intentar registrar un vendedor con el mismo usuario 'test_user'
        response = self.client.post(reverse('crear_vendedor'), {
            'nombre': 'Juan Perez',
            'cedula': '1723456789',
            'telefono': '0999999999',
            'usuario': 'test_user',
            'contrasenia': 'Juan1234'
        })
        # Debe fallar (200 OK en lugar de 302)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vendedor.objects.filter(usuario='test_user').count(), 0)

    def test_postulacion_and_aprobacion_flow(self):
        from django.contrib.auth.hashers import make_password
        # 1. Crear Proveedor, Vendedor y Producto
        proveedor = Proveedor.objects.create(
            nombre="Coca-Cola Test", ruc="1791111117001", direccion="UIO",
            usuario="cocacola_test", contrasenia=make_password("CocaCola1")
        )
        vendedor_bueno = Vendedor.objects.create(
            nombre="Carlos Pérez", cedula="1725555551", usuario="carlos_bueno_t",
            contrasenia=make_password("VendedorGood1"), reputacion="Excelente", calificacion=4.90
        )
        vendedor_malo = Vendedor.objects.create(
            nombre="Juan Rodríguez", cedula="1725555552", usuario="juan_malo_t",
            contrasenia=make_password("VendedorBad1"), reputacion="Mala", calificacion=2.10
        )
        producto = Producto.objects.create(
            nombre="Coca-Cola 1.5L", descripcion="Refresco", cantidad=10, precio=1.50, proveedor=proveedor
        )

        # 2. Iniciar sesión como carlos_bueno_t
        response = self.client.post(reverse('login_role'), {
            'usuario': 'carlos_bueno_t',
            'contrasenia': 'VendedorGood1'
        })
        self.assertEqual(response.status_code, 302)

        # 3. Postularse al producto
        from .models import Postulacion
        response = self.client.post(reverse('postular_producto', args=[producto.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Postulacion.objects.filter(vendedor=vendedor_bueno, producto=producto).count(), 1)
        postulacion_bueno = Postulacion.objects.get(vendedor=vendedor_bueno, producto=producto)
        self.assertEqual(postulacion_bueno.estado, 'Pendiente')

        # 4. Cerrar sesión y entrar como juan_malo_t
        self.client.get(reverse('logout_role'))
        response = self.client.post(reverse('login_role'), {
            'usuario': 'juan_malo_t',
            'contrasenia': 'VendedorBad1'
        })
        self.assertEqual(response.status_code, 302)

        # 5. Postularse al producto
        response = self.client.post(reverse('postular_producto', args=[producto.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Postulacion.objects.filter(vendedor=vendedor_malo, producto=producto).count(), 1)
        postulacion_malo = Postulacion.objects.get(vendedor=vendedor_malo, producto=producto)
        self.assertEqual(postulacion_malo.estado, 'Pendiente')

        # 6. Iniciar sesión como Proveedor
        self.client.get(reverse('logout_role'))
        response = self.client.post(reverse('login_role'), {
            'usuario': 'cocacola_test',
            'contrasenia': 'CocaCola1'
        })
        self.assertEqual(response.status_code, 302)

        # 7. Aprobar postulación de carlos_bueno_t
        response = self.client.post(reverse('aprobar_postulacion', args=[postulacion_bueno.id]))
        self.assertEqual(response.status_code, 302)

        # 8. Verificar que el producto tiene a carlos_bueno_t como vendedor
        producto.refresh_from_db()
        self.assertEqual(producto.vendedor, vendedor_bueno)

        # 9. Verificar que postulacion_bueno está Aprobado y postulacion_malo está Rechazado
        postulacion_bueno.refresh_from_db()
        postulacion_malo.refresh_from_db()
        self.assertEqual(postulacion_bueno.estado, 'Aprobado')
        self.assertEqual(postulacion_malo.estado, 'Rechazado')

    def test_compra_cantidad_personalizada(self):
        from django.contrib.auth.hashers import make_password
        # 1. Crear Comprador y Producto
        comprador = Comprador.objects.create(
            nombre="Don Pepe", cedula="1725555553", direccion="UIO",
            usuario="don_pepe_t", contrasenia=make_password("DonPepe123")
        )
        producto = Producto.objects.create(
            nombre="Coca-Cola 1.5L", descripcion="Refresco", cantidad=10, precio=1.50
        )

        # 2. Iniciar sesión como comprador
        response = self.client.post(reverse('login_role'), {
            'usuario': 'don_pepe_t',
            'contrasenia': 'DonPepe123'
        })
        self.assertEqual(response.status_code, 302)

        # 3. Comprar cantidad válida (4 unidades)
        response = self.client.post(reverse('comprar_producto', args=[producto.id]), {'cantidad': 4})
        self.assertEqual(response.status_code, 302)

        # Verificar stock y pedido
        producto.refresh_from_db()
        self.assertEqual(producto.cantidad, 6)
        self.assertEqual(Pedido.objects.count(), 1)
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.cantidad, 4)
        self.assertEqual(pedido.obtener_total(), Decimal('6.00'))

        # 4. Intentar comprar más que el stock (7 unidades cuando queda 6)
        response = self.client.post(reverse('comprar_producto', args=[producto.id]), {'cantidad': 7})
        self.assertEqual(response.status_code, 302)

        # Verificar que el stock sigue siendo 6 y no se ha creado otro pedido
        producto.refresh_from_db()
        self.assertEqual(producto.cantidad, 6)
        self.assertEqual(Pedido.objects.count(), 1)

    def test_solicitar_vendedor(self):
        from django.contrib.auth.hashers import make_password
        # 1. Crear Proveedor y Producto
        proveedor = Proveedor.objects.create(
            nombre="Alpina Proveedor", ruc="1792345677001", direccion="Quito",
            usuario="alpina_p", contrasenia=make_password("Alpina123")
        )
        producto = Producto.objects.create(
            nombre="Leche Descremada", descripcion="Leche", cantidad=50, precio=1.10, proveedor=proveedor
        )
        
        # 2. Iniciar sesión como Proveedor
        response = self.client.post(reverse('login_role'), {
            'usuario': 'alpina_p',
            'contrasenia': 'Alpina123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 3. Enviar solicitud de vendedor para el producto
        response = self.client.post(reverse('solicitar_vendedor', args=[producto.id]))
        self.assertEqual(response.status_code, 302)
        
        # 4. Verificar que se activó la solicitud de vendedor
        producto.refresh_from_db()
        self.assertTrue(producto.solicitud_vendedor_activa)


