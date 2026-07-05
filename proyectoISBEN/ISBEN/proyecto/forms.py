from django.forms import ModelForm
from django import forms
from .models import Proveedor, Vendedor, Comprador, Producto

class ProveedorForm(ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'direccion']

class VendedorForm(ModelForm):
    class Meta:
        model = Vendedor
        fields = ['nombre', 'cedula', 'telefono']

class CompradorForm(ModelForm):
    class Meta:
        model = Comprador
        fields = ['nombre', 'cedula', 'direccion']

class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'cantidad', 'precio', 'proveedor', 'vendedor']
