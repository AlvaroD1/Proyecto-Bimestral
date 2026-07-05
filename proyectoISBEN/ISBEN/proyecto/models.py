from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=13, unique=True)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return "%s - %s" % (self.nombre, self.ruc)

    def obtener_productos(self):
        return self.productos.all()

    def obtener_pedidos(self):
        return Pedido.objects.filter(producto__proveedor=self).order_by('-fecha')

    def obtener_cantidad_productos(self):
        return self.productos.count()

    class Meta:
        verbose_name_plural = "Proveedores"

class Vendedor(models.Model):
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.nombre, self.cedula)

    def obtener_productos(self):
        return self.productos.all()

    def obtener_pedidos(self):
        return Pedido.objects.filter(producto__vendedor=self).order_by('-fecha')

    class Meta:
        verbose_name_plural = "Vendedores"

class Comprador(models.Model):
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return "%s - %s" % (self.nombre, self.cedula)

    def obtener_pedidos(self):
        return self.pedidos.all().order_by('-fecha')

    def obtener_total_gastado(self):
        return sum(pedido.obtener_total() for pedido in self.pedidos.all())

    class Meta:
        verbose_name_plural = "Compradores"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    cantidad = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="productos", null=True, blank=True)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name="productos", null=True, blank=True)

    def __str__(self):
        return "%s (Stock: %d)" % (self.nombre, self.cantidad)

    def tiene_stock(self):
        return self.cantidad > 0

class Pedido(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Enviado', 'Enviado'),
        ('Recibido', 'Recibido'),
    ]
    comprador = models.ForeignKey(Comprador, on_delete=models.CASCADE, related_name="pedidos")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="pedidos")
    cantidad = models.IntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Pedido #%d - %s (%s)" % (self.id, self.producto.nombre, self.estado)

    def obtener_total(self):
        return self.cantidad * self.producto.precio
