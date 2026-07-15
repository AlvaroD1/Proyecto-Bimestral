from django.db import models
from django.core.exceptions import ValidationError
import uuid

def validar_ruc_ecuador(value):
    if not value or len(value) != 13 or not value.isdigit():
        raise ValidationError("El RUC debe tener exactamente 13 dígitos numéricos.")
    
    provincia = int(value[:2])
    if provincia < 1 or provincia > 24:
        raise ValidationError("El código de provincia (primeros dos dígitos) debe estar entre 01 y 24.")
        
    tipo = int(value[2])
    if tipo not in [0, 1, 2, 3, 4, 5, 6, 9]:
        raise ValidationError("El tercer dígito del RUC debe ser del 0 al 5 (personas naturales), 6 (públicas) o 9 (privadas).")
        
    if value[10:] != "001":
        raise ValidationError("El RUC debe terminar en 001.")
        
    # Persona Natural (0 al 5)
    if 0 <= tipo <= 5:
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        for i in range(9):
            val = int(value[i]) * coeficientes[i]
            if val >= 10:
                val -= 9
            suma += val
        verificador = (10 - (suma % 10)) % 10
        if verificador != int(value[9]):
            raise ValidationError("El RUC de persona natural no supera la validación del dígito verificador.")
        
    # Sociedad Privada (9)
    elif tipo == 9:
        coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = 0
        for i in range(9):
            suma += int(value[i]) * coeficientes[i]
        verificador = 11 - (suma % 11)
        if verificador == 11:
            verificador = 0
        elif verificador == 10:
            raise ValidationError("Dígito verificador inválido para sociedad privada.")
        if verificador != int(value[9]):
            raise ValidationError("El RUC de sociedad privada no supera la validación del dígito verificador.")
        
    # Sociedad Pública (6)
    elif tipo == 6:
        coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
        suma = 0
        for i in range(8):
            suma += int(value[i]) * coeficientes[i]
        verificador = 11 - (suma % 11)
        if verificador == 11:
            verificador = 0
        elif verificador == 10:
            raise ValidationError("Dígito verificador inválido para sociedad pública.")
        if verificador != int(value[8]):
            raise ValidationError("El RUC de sociedad pública no supera la validación del dígito verificador.")

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=13, unique=True, validators=[validar_ruc_ecuador])
    direccion = models.CharField(max_length=200)
    usuario = models.CharField(max_length=100, unique=True, null=True, blank=True)
    contrasenia = models.CharField(max_length=128, null=True, blank=True)

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
    usuario = models.CharField(max_length=100, unique=True, null=True, blank=True)
    contrasenia = models.CharField(max_length=128, null=True, blank=True)
    reputacion = models.CharField(max_length=50, default='Buena')
    calificacion = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    descripcion_perfil = models.TextField(blank=True, null=True)

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
    usuario = models.CharField(max_length=100, unique=True, null=True, blank=True)
    contrasenia = models.CharField(max_length=128, null=True, blank=True)

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
    solicitud_vendedor_activa = models.BooleanField(default=False)

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
    PORCENTAJE_CHOICES = [
        (100, 'Pago completo (100%)'),
        (50, 'Pago parcial (50%)'),
    ]
    METODO_PAGO_CHOICES = [
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('transferencia', 'Transferencia Bancaria'),
    ]
    comprador = models.ForeignKey(Comprador, on_delete=models.CASCADE, related_name="pedidos")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="pedidos")
    cantidad = models.IntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    fecha = models.DateTimeField(auto_now_add=True)
    # Campos de pago
    porcentaje_pago = models.IntegerField(choices=PORCENTAJE_CHOICES, default=100)
    metodo_pago = models.CharField(max_length=30, choices=METODO_PAGO_CHOICES, default='tarjeta_credito')
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pago_completado = models.BooleanField(default=True)
    # Campos de entrega segura
    codigo_entrega = models.CharField(max_length=6, blank=True, null=True)
    entrega_confirmada = models.BooleanField(default=False)
    fecha_entrega = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Pedido #%d - %s (%s)" % (self.id, self.producto.nombre, self.estado)

    def obtener_total(self):
        return self.cantidad * self.producto.precio

    @staticmethod
    def generar_codigo():
        return uuid.uuid4().hex[:6].upper()

class Postulacion(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
    ]
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name="postulaciones")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="postulaciones")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vendedor', 'producto')
        verbose_name_plural = "Postulaciones"

    def __str__(self):
        return f"Postulación de {self.vendedor.nombre} para {self.producto.nombre} ({self.estado})"
