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
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfiles/proveedores/', blank=True, null=True)
    pagina_web = models.URLField(blank=True, null=True, help_text="Página web oficial de la empresa.")
    red_facebook = models.URLField(blank=True, null=True, help_text="Link de Facebook.")
    red_instagram = models.URLField(blank=True, null=True, help_text="Link de Instagram.")
    red_linkedin = models.URLField(blank=True, null=True, help_text="Link de LinkedIn.")
    red_twitter = models.URLField(blank=True, null=True, help_text="Link de Twitter / X.")

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
<<<<<<< HEAD
    latitud_actual = models.FloatField(blank=True, null=True, help_text="Latitud actual para rastreo en tiempo real")
    longitud_actual = models.FloatField(blank=True, null=True, help_text="Longitud actual para rastreo en tiempo real")
=======
    foto_perfil = models.ImageField(upload_to='perfiles/vendedores/', blank=True, null=True)
    acepta_letras_cambio = models.BooleanField(default=False, help_text="Indica si el vendedor acepta ofrecer letras de cambio / crédito a compradores.")
>>>>>>> a8c57b0 (Perfiles para cada Rol)

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
<<<<<<< HEAD
    latitud = models.FloatField(blank=True, null=True, help_text="Latitud de la tienda")
    longitud = models.FloatField(blank=True, null=True, help_text="Longitud de la tienda")
    referencias_direccion = models.TextField(blank=True, null=True, help_text="Puntos de referencia para llegar")
=======
    telefono = models.CharField(max_length=15, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfiles/compradores/', blank=True, null=True)
>>>>>>> a8c57b0 (Perfiles para cada Rol)

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
    stock_minimo = models.IntegerField(default=5, help_text="Umbral mínimo de stock para generar alertas de reposición.")

    def __str__(self):
        return "%s (Stock: %d)" % (self.nombre, self.cantidad)

    def tiene_stock(self):
        return self.cantidad > 0

    def stock_bajo(self):
        """Retorna True si el stock actual está en o por debajo del umbral mínimo."""
        return self.cantidad <= self.stock_minimo

    def obtener_descuentos(self):
        """Retorna los descuentos por volumen del producto, ordenados por cantidad mínima."""
        return self.descuentos_volumen.all().order_by('cantidad_minima')


class DescuentoVolumen(models.Model):
    """Descuento automático al comprar cierta cantidad mínima de un producto."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="descuentos_volumen")
    cantidad_minima = models.IntegerField(help_text="Cantidad mínima de unidades para aplicar el descuento.")
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje de descuento (ej: 5.00 para 5%).")
    descripcion = models.CharField(max_length=200, blank=True, null=True, help_text="Descripción opcional del descuento.")

    class Meta:
        verbose_name = "Descuento por Volumen"
        verbose_name_plural = "Descuentos por Volumen"
        unique_together = ('producto', 'cantidad_minima')
        ordering = ['cantidad_minima']

    def __str__(self):
        return f"{self.porcentaje_descuento}% descuento en {self.producto.nombre} (≥{self.cantidad_minima} uds.)"


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
    # Snapshot del precio al momento de la compra (no cambia si se edita el producto después)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text="Precio unitario congelado al momento de crear el pedido.")
    # Campos de descuento por volumen
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text="Monto total de descuento aplicado en este pedido.")
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0,
        help_text="Porcentaje de descuento aplicado (ej: 5.00 para 5%).")
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
        """Calcula el total usando el precio congelado y aplicando descuento."""
        subtotal = self.cantidad * self.precio_unitario
        return subtotal - self.descuento_aplicado

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


# ========== INVENTARIO DE TIENDA DEL TENDERO (COMPRADOR) ==========

class InventarioTienda(models.Model):
    """Rastrea el stock propio de la tienda del tendero (comprador)."""
    comprador = models.ForeignKey(Comprador, on_delete=models.CASCADE, related_name="inventario_tienda")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="inventarios_tienda")
    cantidad = models.IntegerField(default=0, help_text="Stock actual en la tienda del tendero.")
    stock_minimo = models.IntegerField(default=5, help_text="Umbral mínimo de stock para generar alertas.")

    class Meta:
        verbose_name = "Inventario de Tienda"
        verbose_name_plural = "Inventarios de Tienda"
        unique_together = ('comprador', 'producto')

    def __str__(self):
        return f"{self.producto.nombre} en tienda de {self.comprador.nombre} ({self.cantidad} uds.)"

    def stock_bajo(self):
        """Retorna True si el stock actual está en o por debajo del umbral mínimo."""
        return self.cantidad <= self.stock_minimo


# ========== SISTEMA DE ALERTAS DE STOCK Y REPOSICIÓN ==========

class ListaReposicion(models.Model):
    ESTADOS = [
        ('Borrador', 'Borrador'),
        ('Enviada', 'Enviada'),
    ]
    comprador = models.ForeignKey(Comprador, on_delete=models.CASCADE, related_name="listas_reposicion")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Borrador')
    notas = models.TextField(blank=True, null=True, help_text="Notas adicionales para el proveedor.")

    class Meta:
        verbose_name = "Lista de Reposición"
        verbose_name_plural = "Listas de Reposición"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Lista #{self.id} - {self.comprador.nombre} ({self.estado})"

    def obtener_total_items(self):
        return self.items.count()

    def obtener_items_por_proveedor(self):
        """Agrupa los ítems por proveedor para facilitar el envío."""
        from collections import defaultdict
        agrupados = defaultdict(list)
        for item in self.items.select_related('producto', 'producto__proveedor').all():
            proveedor_nombre = item.producto.proveedor.nombre if item.producto.proveedor else "Sin proveedor"
            agrupados[proveedor_nombre].append(item)
        return dict(agrupados)


class ItemReposicion(models.Model):
    lista = models.ForeignKey(ListaReposicion, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="items_reposicion")
    cantidad_solicitada = models.IntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ítem de Reposición"
        verbose_name_plural = "Ítems de Reposición"
        unique_together = ('lista', 'producto')

    def __str__(self):
        return f"{self.cantidad_solicitada}x {self.producto.nombre}"


# ========== INTEGRACIÓN CON FACTURACIÓN (EN ESPERA) ==========

class ConfiguracionFacturacion(models.Model):
    """
    Modelo preparado para futuras integraciones con sistemas de facturación
    de los tenderos. Actualmente EN ESPERA - no activo.
    """
    TIPOS_SISTEMA = [
        ('ninguno', 'Ninguno'),
        ('sri_ecuador', 'SRI Ecuador (Facturación Electrónica)'),
        ('otro_erp', 'Otro ERP / Sistema Contable'),
        ('personalizado', 'API Personalizada'),
    ]
    comprador = models.OneToOneField(Comprador, on_delete=models.CASCADE, related_name="config_facturacion")
    sistema_activo = models.BooleanField(default=False, help_text="Indica si el tendero tiene un sistema de facturación conectado.")
    tipo_sistema = models.CharField(max_length=30, choices=TIPOS_SISTEMA, default='ninguno')
    url_api = models.URLField(blank=True, null=True, help_text="URL del API del sistema de facturación (futuro).")
    api_key = models.CharField(max_length=255, blank=True, null=True, help_text="Clave de API (futuro).")
    ultimo_sync = models.DateTimeField(blank=True, null=True, help_text="Última sincronización exitosa.")

    class Meta:
        verbose_name = "Configuración de Facturación"
        verbose_name_plural = "Configuraciones de Facturación"

    def __str__(self):
        estado = "Activo" if self.sistema_activo else "Inactivo"
        return f"Facturación {self.comprador.nombre} - {estado}"

