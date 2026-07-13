from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Proveedor, Vendedor, Comprador, Producto, Pedido
from .forms import ProveedorForm, VendedorForm, CompradorForm, ProductoForm

def index(request):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role and role_id:
        if role == 'proveedor':
            return redirect('dashboard_proveedor')
        elif role == 'vendedor':
            return redirect('dashboard_vendedor')
        elif role == 'comprador':
            return redirect('dashboard_comprador')

    return render(request, 'index.html')

def login_role(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')
        
        if not usuario or not contrasenia:
            messages.error(request, "Por favor ingrese su usuario y contraseña.")
            return redirect('index')
            
        user_obj = None
        role = None
        
        # Check Proveedor
        prov = Proveedor.objects.filter(usuario=usuario).first()
        if prov and check_password(contrasenia, prov.contrasenia):
            user_obj = prov
            role = 'proveedor'
            
        # Check Vendedor
        if not user_obj:
            vend = Vendedor.objects.filter(usuario=usuario).first()
            if vend and check_password(contrasenia, vend.contrasenia):
                user_obj = vend
                role = 'vendedor'
                
        # Check Comprador
        if not user_obj:
            comp = Comprador.objects.filter(usuario=usuario).first()
            if comp and check_password(contrasenia, comp.contrasenia):
                user_obj = comp
                role = 'comprador'
                
        if user_obj:
            request.session['role'] = role
            request.session['role_id'] = user_obj.id
            request.session['role_name'] = user_obj.nombre
            messages.success(request, f"¡Sesión iniciada como {role.capitalize()}: {user_obj.nombre}!")
            if role == 'proveedor':
                return redirect('dashboard_proveedor')
            elif role == 'vendedor':
                return redirect('dashboard_vendedor')
            elif role == 'comprador':
                return redirect('dashboard_comprador')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            
    return redirect('index')

def logout_role(request):
    role = request.session.pop('role', None)
    request.session.pop('role_id', None)
    request.session.pop('role_name', None)
    if role:
        messages.info(request, "Sesión cerrada correctamente.")
    return redirect('index')


def dashboard_proveedor(request):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'proveedor' or not role_id:
        return redirect('index')
    
    proveedor = get_object_or_404(Proveedor, pk=role_id)
    # Hacerle preguntas al modelo directamente para obtener info
    productos = proveedor.obtener_productos()
    pedidos = proveedor.obtener_pedidos()
    
    contexto = {
        'proveedor': proveedor,
        'productos': productos,
        'pedidos': pedidos,
    }
    return render(request, 'dashboard_proveedor.html', contexto)

def dashboard_vendedor(request):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'vendedor' or not role_id:
        return redirect('index')
    
    vendedor = get_object_or_404(Vendedor, pk=role_id)
    # Hacerle preguntas al modelo directamente para obtener info
    productos = vendedor.obtener_productos()
    pedidos = vendedor.obtener_pedidos()
    
    contexto = {
        'vendedor': vendedor,
        'productos': productos,
        'pedidos': pedidos,
    }
    return render(request, 'dashboard_vendedor.html', contexto)

def dashboard_comprador(request):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'comprador' or not role_id:
        return redirect('index')
    
    comprador = get_object_or_404(Comprador, pk=role_id)
    # Hacerle preguntas al modelo directamente para obtener info
    pedidos = comprador.obtener_pedidos()
    productos = Producto.objects.all()
    
    contexto = {
        'comprador': comprador,
        'productos': productos,
        'pedidos': pedidos,
        'total_gastado': comprador.obtener_total_gastado(),
    }
    return render(request, 'dashboard_comprador.html', contexto)

# Crear perfiles
def crear_proveedor(request):
    if request.method == 'POST':
        formulario = ProveedorForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('index')
    else:
        formulario = ProveedorForm()
    return render(request, 'crear_proveedor.html', {'formulario': formulario})

def crear_vendedor(request):
    if request.method == 'POST':
        formulario = VendedorForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('index')
    else:
        formulario = VendedorForm()
    return render(request, 'crear_vendedor.html', {'formulario': formulario})

def crear_comprador(request):
    if request.method == 'POST':
        formulario = CompradorForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('index')
    else:
        formulario = CompradorForm()
    return render(request, 'crear_comprador.html', {'formulario': formulario})

# CRUD Productos
def crear_producto(request):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if not role or not role_id:
        return redirect('index')
        
    if request.method == 'POST':
        formulario = ProductoForm(request.POST)
        if formulario.is_valid():
            producto = formulario.save(commit=False)
            if role == 'proveedor':
                producto.proveedor = Proveedor.objects.get(pk=role_id)
            elif role == 'vendedor':
                producto.vendedor = Vendedor.objects.get(pk=role_id)
            producto.save()
            return redirect('index')
    else:
        initial = {}
        if role == 'proveedor':
            initial['proveedor'] = role_id
        elif role == 'vendedor':
            initial['vendedor'] = role_id
        formulario = ProductoForm(initial=initial)
        
    return render(request, 'crear_producto.html', {'formulario': formulario})

def editar_producto(request, id):
    role = request.session.get('role')
    if not role:
        return redirect('index')
        
    producto = get_object_or_404(Producto, pk=id)
    if request.method == 'POST':
        formulario = ProductoForm(request.POST, instance=producto)
        if formulario.is_valid():
            formulario.save()
            return redirect('index')
    else:
        formulario = ProductoForm(instance=producto)
    return render(request, 'editar_producto.html', {'formulario': formulario})

def eliminar_producto(request, id):
    role = request.session.get('role')
    if not role:
        return redirect('index')
        
    producto = get_object_or_404(Producto, pk=id)
    producto.delete()
    messages.success(request, f"Producto {producto.nombre} eliminado.")
    return redirect('index')

# Pedidos / Flujos de Transacción
def comprar_producto(request, id):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'comprador' or not role_id:
        return redirect('index')
        
    comprador = get_object_or_404(Comprador, pk=role_id)
    producto = get_object_or_404(Producto, pk=id)
    
    # Preguntar al modelo Producto si tiene stock
    if producto.tiene_stock():
        producto.cantidad -= 1
        producto.save()
        
        # Crear el Pedido en estado Pendiente
        Pedido.objects.create(
            comprador=comprador,
            producto=producto,
            cantidad=1,
            estado='Pendiente'
        )
        
        messages.success(request, f"Pedido realizado para 1 unidad de {producto.nombre}. Estado: PENDIENTE")
    else:
        messages.error(request, f"No hay stock disponible para {producto.nombre}")
        
    return redirect('dashboard_comprador')

def enviar_pedido(request, id):
    role = request.session.get('role')
    if role not in ['proveedor', 'vendedor']:
        return redirect('index')
        
    pedido = get_object_or_404(Pedido, pk=id)
    if pedido.estado == 'Pendiente':
        pedido.estado = 'Enviado'
        pedido.save()
        messages.success(request, f"El pedido #{pedido.id} ha sido despachado / enviado.")
    else:
        messages.error(request, f"El pedido #{pedido.id} no se puede enviar porque está en estado {pedido.estado}.")
        
    return redirect('index')

def recibir_pedido(request, id):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'comprador' or not role_id:
        return redirect('index')
        
    pedido = get_object_or_404(Pedido, pk=id)
    # Validar que pertenezca al comprador activo
    if pedido.comprador.id != role_id:
        messages.error(request, "Acceso no autorizado a este pedido.")
        return redirect('index')
        
    if pedido.estado in ['Pendiente', 'Enviado']:
        pedido.estado = 'Recibido'
        pedido.save()
        messages.success(request, f"Has marcado el pedido #{pedido.id} como RECIBIDO. ¡Gracias!")
    else:
        messages.error(request, f"El pedido ya está en estado {pedido.estado}.")
        
    return redirect('dashboard_comprador')
