from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=13, unique=True)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return "%s - %s" % (self.nombre, self.ruc)

    class Meta:
        verbose_name_plural = "Proveedores"

class Vendedor(models.Model):
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.nombre, self.cedula)

    class Meta:
        verbose_name_plural = "Vendedores"

class Comprador(models.Model):
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return "%s - %s" % (self.nombre, self.cedula)

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
