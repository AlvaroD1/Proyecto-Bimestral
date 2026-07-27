from django import forms
from django.contrib.auth.hashers import make_password
from .models import Proveedor, Vendedor, Comprador, Producto, ItemReposicion, ConfiguracionFacturacion
import os

def validar_usuario_unico(usuario, current_id=None, current_role=None):
    # Check Proveedor (exclude current if role matches)
    prov_qs = Proveedor.objects.filter(usuario=usuario)
    if current_role == 'proveedor' and current_id:
        prov_qs = prov_qs.exclude(id=current_id)
    if prov_qs.exists():
        return False

    # Check Vendedor (exclude current if role matches)
    vend_qs = Vendedor.objects.filter(usuario=usuario)
    if current_role == 'vendedor' and current_id:
        vend_qs = vend_qs.exclude(id=current_id)
    if vend_qs.exists():
        return False

    # Check Comprador (exclude current if role matches)
    comp_qs = Comprador.objects.filter(usuario=usuario)
    if current_role == 'comprador' and current_id:
        comp_qs = comp_qs.exclude(id=current_id)
    if comp_qs.exists():
        return False

    return True

def validar_contrasenia_fuerte(contrasenia):
    tiene_mayuscula = any(c.isupper() for c in contrasenia)
    tiene_minuscula = any(c.islower() for c in contrasenia)
    tiene_numero = any(c.isdigit() for c in contrasenia)
    return tiene_mayuscula and tiene_minuscula and tiene_numero

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'direccion', 'usuario', 'contrasenia']
        widgets = {
            'contrasenia': forms.PasswordInput(),
        }
        labels = {
            'nombre': 'Nombre / Razón Social',
            'ruc': 'RUC',
            'direccion': 'Dirección',
            'usuario': 'Nombre de Usuario',
            'contrasenia': 'Contraseña',
        }

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if not usuario:
            raise forms.ValidationError("El nombre de usuario es obligatorio.")
        
        current_id = self.instance.id if self.instance and self.instance.id else None
        if not validar_usuario_unico(usuario, current_id, 'proveedor'):
            raise forms.ValidationError("Este nombre de usuario ya está registrado por otro usuario.")
        return usuario

    def clean_contrasenia(self):
        contrasenia = self.cleaned_data.get('contrasenia')
        if not contrasenia:
            raise forms.ValidationError("La contraseña es obligatoria.")
        
        if not validar_contrasenia_fuerte(contrasenia):
            raise forms.ValidationError(
                "La contraseña debe contener al menos una letra mayúscula, una letra minúscula y un número."
            )
        return contrasenia

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.contrasenia = make_password(self.cleaned_data['contrasenia'])
        if commit:
            instance.save()
        return instance

class VendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ['nombre', 'cedula', 'telefono', 'usuario', 'contrasenia', 'acepta_letras_cambio']
        widgets = {
            'contrasenia': forms.PasswordInput(),
            'acepta_letras_cambio': forms.CheckboxInput(),
        }
        labels = {
            'nombre': 'Nombre Completo',
            'cedula': 'Cédula',
            'telefono': 'Teléfono',
            'usuario': 'Nombre de Usuario',
            'contrasenia': 'Contraseña',
            'acepta_letras_cambio': 'Acepto ofrecer letras de cambio / crédito a compradores',
        }

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if not usuario:
            raise forms.ValidationError("El nombre de usuario es obligatorio.")
        
        current_id = self.instance.id if self.instance and self.instance.id else None
        if not validar_usuario_unico(usuario, current_id, 'vendedor'):
            raise forms.ValidationError("Este nombre de usuario ya está registrado por otro usuario.")
        return usuario

    def clean_contrasenia(self):
        contrasenia = self.cleaned_data.get('contrasenia')
        if not contrasenia:
            raise forms.ValidationError("La contraseña es obligatoria.")
        
        if not validar_contrasenia_fuerte(contrasenia):
            raise forms.ValidationError(
                "La contraseña debe contener al menos una letra mayúscula, una letra minúscula y un número."
            )
        return contrasenia

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.contrasenia = make_password(self.cleaned_data['contrasenia'])
        if commit:
            instance.save()
        return instance

class CompradorForm(forms.ModelForm):
    tiene_facturacion = forms.BooleanField(
        required=False,
        initial=False,
        label='¿Cuenta con un sistema de facturación?',
        help_text='Active esta opción si su tienda cuenta con un sistema de facturación electrónica o contable que desee integrar.',
        widget=forms.CheckboxInput(attrs={'class': 'toggle-checkbox'}),
    )

    class Meta:
        model = Comprador
        fields = ['nombre', 'cedula', 'direccion', 'referencias_direccion', 'usuario', 'contrasenia', 'latitud', 'longitud']
        widgets = {
            'contrasenia': forms.PasswordInput(),
            'latitud': forms.HiddenInput(attrs={'id': 'id_latitud'}),
            'longitud': forms.HiddenInput(attrs={'id': 'id_longitud'}),
            'referencias_direccion': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ej. Cerca del parque central...'}),
        }
        labels = {
            'nombre': 'Nombre Completo',
            'cedula': 'Cédula',
            'direccion': 'Dirección principal',
            'referencias_direccion': 'Puntos de Referencia',
            'usuario': 'Nombre de Usuario',
            'contrasenia': 'Contraseña',
        }

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if not usuario:
            raise forms.ValidationError("El nombre de usuario es obligatorio.")
        
        current_id = self.instance.id if self.instance and self.instance.id else None
        if not validar_usuario_unico(usuario, current_id, 'comprador'):
            raise forms.ValidationError("Este nombre de usuario ya está registrado por otro usuario.")
        return usuario

    def clean_contrasenia(self):
        contrasenia = self.cleaned_data.get('contrasenia')
        if not contrasenia:
            raise forms.ValidationError("La contraseña es obligatoria.")
        
        if not validar_contrasenia_fuerte(contrasenia):
            raise forms.ValidationError(
                "La contraseña debe contener al menos una letra mayúscula, una letra minúscula y un número."
            )
        return contrasenia

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.contrasenia = make_password(self.cleaned_data['contrasenia'])
        if commit:
            instance.save()
        return instance

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'cantidad', 'precio', 'stock_minimo']
        labels = {
            'stock_minimo': 'Stock Mínimo (Umbral de alerta)',
        }
        help_texts = {
            'stock_minimo': 'Cuando el stock llegue a este número o menos, se generará una alerta de reposición.',
        }


class ItemReposicionForm(forms.Form):
    """Formulario simple para agregar un producto a la lista de reposición."""
    cantidad = forms.IntegerField(
        min_value=1,
        initial=10,
        label='Cantidad a solicitar',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 80px; text-align: center;',
            'min': '1',
        })
    )


# ========== VALIDACIÓN DE IMÁGENES ==========

FORMATOS_IMAGEN_VALIDOS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
MAX_TAMANO_IMAGEN_MB = 5  # Tamaño máximo en megabytes

def validar_formato_imagen(imagen):
    """Valida formato y peso del archivo de imagen subido."""
    if imagen:
        # Validar extensión
        ext = os.path.splitext(imagen.name)[1].lower()
        if ext not in FORMATOS_IMAGEN_VALIDOS:
            raise forms.ValidationError(
                f"Formato no permitido ({ext}). "
                f"Formatos válidos: {', '.join(FORMATOS_IMAGEN_VALIDOS)}"
            )
        
        # Validar tamaño máximo (5 MB)
        if imagen.size > MAX_TAMANO_IMAGEN_MB * 1024 * 1024:
            raise forms.ValidationError(
                f"El archivo pesa demasiado ({round(imagen.size / (1024 * 1024), 2)} MB). "
                f"El tamaño máximo permitido es de {MAX_TAMANO_IMAGEN_MB} MB."
            )



# ========== FORMULARIOS DE PERFIL ==========

class PerfilCompradorForm(forms.ModelForm):
    sistema_facturacion = forms.BooleanField(
        required=False,
        label='¿Tiene sistema de facturación activo?',
        help_text='Habilite o deshabilite la integración con su sistema de facturación.',
        widget=forms.CheckboxInput(attrs={'class': 'toggle-checkbox'}),
    )

    class Meta:
        model = Comprador
        fields = ['nombre', 'cedula', 'direccion', 'telefono', 'foto_perfil']
        labels = {
            'nombre': 'Nombre Completo',
            'cedula': 'Cédula',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'foto_perfil': 'Foto de Perfil',
        }
        widgets = {
            'foto_perfil': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def clean_foto_perfil(self):
        imagen = self.cleaned_data.get('foto_perfil')
        validar_formato_imagen(imagen)
        return imagen


class PerfilVendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ['nombre', 'cedula', 'telefono', 'descripcion_perfil', 'foto_perfil', 'acepta_letras_cambio']
        labels = {
            'nombre': 'Nombre Completo',
            'cedula': 'Cédula',
            'telefono': 'Teléfono',
            'descripcion_perfil': 'Descripción del Perfil',
            'foto_perfil': 'Foto de Perfil',
            'acepta_letras_cambio': 'Acepto ofrecer letras de cambio / crédito a compradores',
        }
        widgets = {
            'foto_perfil': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'descripcion_perfil': forms.Textarea(attrs={'rows': 4}),
            'acepta_letras_cambio': forms.CheckboxInput(),
        }

    def clean_foto_perfil(self):
        imagen = self.cleaned_data.get('foto_perfil')
        validar_formato_imagen(imagen)
        return imagen


class PerfilProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre', 'ruc', 'direccion', 'telefono', 'email', 'foto_perfil',
            'pagina_web', 'red_facebook', 'red_instagram', 'red_linkedin', 'red_twitter',
        ]
        labels = {
            'nombre': 'Nombre / Razón Social',
            'ruc': 'RUC',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'foto_perfil': 'Logo / Foto de la Empresa',
            'pagina_web': 'Página Web Oficial',
            'red_facebook': 'Facebook',
            'red_instagram': 'Instagram',
            'red_linkedin': 'LinkedIn',
            'red_twitter': 'Twitter / X',
        }
        widgets = {
            'foto_perfil': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def clean_foto_perfil(self):
        imagen = self.cleaned_data.get('foto_perfil')
        validar_formato_imagen(imagen)
        return imagen
