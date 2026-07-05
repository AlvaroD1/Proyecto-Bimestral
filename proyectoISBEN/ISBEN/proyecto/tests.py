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
            'ruc': '1792345678001',
            'direccion': 'Av. Amazonas 123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Proveedor.objects.count(), 1)
        proveedor = Proveedor.objects.first()
        self.assertEqual(proveedor.nombre, 'Distribuidora Alpina')

        # 2. Registrar Vendedor
        response = self.client.post(reverse('crear_vendedor'), {
            'nombre': 'Juan Perez',
            'cedula': '1723456789',
            'telefono': '0999999999'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vendedor.objects.count(), 1)
        vendedor = Vendedor.objects.first()

        # 3. Registrar Comprador
        response = self.client.post(reverse('crear_comprador'), {
            'nombre': 'Tienda Don Bosco',
            'cedula': '1712345678',
            'direccion': 'Calle Loja y Sucre'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comprador.objects.count(), 1)
        comprador = Comprador.objects.first()

        # 4. Iniciar sesión como Proveedor
        response = self.client.post(reverse('login_role'), {
            'role': 'proveedor',
            'role_id': proveedor.id
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
            'role': 'comprador',
            'role_id': comprador.id
        })
        self.assertEqual(response.status_code, 302)

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
            'role': 'proveedor',
            'role_id': proveedor.id
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
            'role': 'comprador',
            'role_id': comprador.id
        })
        self.assertEqual(response.status_code, 302)
        
        # Recibir pedido
        response = self.client.post(reverse('recibir_pedido', args=[pedido.id]))
        self.assertEqual(response.status_code, 302)
        
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'Recibido')
        
        self.assertEqual(comprador.obtener_total_gastado(), Decimal('1.20'))
