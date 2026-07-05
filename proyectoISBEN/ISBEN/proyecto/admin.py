from django.contrib import admin
from .models import Proveedor, Vendedor, Comprador, Producto, Pedido

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'direccion')
    search_fields = ('nombre', 'ruc')

class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cedula', 'telefono')
    search_fields = ('nombre', 'cedula')

class CompradorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cedula', 'direccion')
    search_fields = ('nombre', 'cedula')

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad', 'precio', 'proveedor', 'vendedor')
    search_fields = ('nombre',)
    list_filter = ('proveedor', 'vendedor')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'comprador', 'producto', 'cantidad', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('comprador__nombre', 'producto__nombre')

admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(Vendedor, VendedorAdmin)
admin.site.register(Comprador, CompradorAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)
