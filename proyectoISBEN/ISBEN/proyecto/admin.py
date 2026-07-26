from django.contrib import admin
from .models import (
    Proveedor, Vendedor, Comprador, Producto, Pedido, Postulacion,
    InventarioTienda, ListaReposicion, ItemReposicion, ConfiguracionFacturacion,
    DescuentoVolumen
)

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'direccion')
    search_fields = ('nombre', 'ruc')

class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cedula', 'telefono', 'reputacion', 'calificacion')
    search_fields = ('nombre', 'cedula')

class CompradorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cedula', 'direccion')
    search_fields = ('nombre', 'cedula')

# ProductoAdmin moved below to be after DescuentoVolumenInline

class DescuentoVolumenInline(admin.TabularInline):
    model = DescuentoVolumen
    extra = 1

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad', 'stock_minimo', 'precio', 'proveedor', 'vendedor')
    search_fields = ('nombre',)
    list_filter = ('proveedor', 'vendedor')
    inlines = [DescuentoVolumenInline]

class DescuentoVolumenAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad_minima', 'porcentaje_descuento', 'descripcion')
    list_filter = ('producto__proveedor',)
    search_fields = ('producto__nombre',)

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'comprador', 'producto', 'cantidad', 'precio_unitario', 'porcentaje_descuento', 'estado', 'fecha')
    list_filter = ('estado', 'fecha', 'pago_completado')
    search_fields = ('comprador__nombre', 'producto__nombre')
    readonly_fields = ('precio_unitario', 'descuento_aplicado', 'porcentaje_descuento')

class PostulacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendedor', 'producto', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('vendedor__nombre', 'producto__nombre')

class ItemReposicionInline(admin.TabularInline):
    model = ItemReposicion
    extra = 0
    readonly_fields = ('fecha_agregado',)

class ListaReposicionAdmin(admin.ModelAdmin):
    list_display = ('id', 'comprador', 'estado', 'fecha_creacion', 'fecha_envio', 'obtener_total_items')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('comprador__nombre',)
    inlines = [ItemReposicionInline]

class ItemReposicionAdmin(admin.ModelAdmin):
    list_display = ('id', 'lista', 'producto', 'cantidad_solicitada', 'fecha_agregado')
    list_filter = ('lista__estado',)
    search_fields = ('producto__nombre',)

class ConfiguracionFacturacionAdmin(admin.ModelAdmin):
    list_display = ('comprador', 'sistema_activo', 'tipo_sistema', 'ultimo_sync')
    list_filter = ('sistema_activo', 'tipo_sistema')
    search_fields = ('comprador__nombre',)

class InventarioTiendaAdmin(admin.ModelAdmin):
    list_display = ('comprador', 'producto', 'cantidad', 'stock_minimo')
    list_filter = ('comprador', 'producto__proveedor')
    search_fields = ('comprador__nombre', 'producto__nombre')

admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(Vendedor, VendedorAdmin)
admin.site.register(Comprador, CompradorAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Postulacion, PostulacionAdmin)
admin.site.register(ListaReposicion, ListaReposicionAdmin)
admin.site.register(ItemReposicion, ItemReposicionAdmin)
admin.site.register(ConfiguracionFacturacion, ConfiguracionFacturacionAdmin)
admin.site.register(InventarioTienda, InventarioTiendaAdmin)
admin.site.register(DescuentoVolumen, DescuentoVolumenAdmin)

