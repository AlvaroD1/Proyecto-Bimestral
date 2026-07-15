from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from decimal import Decimal
from .models import Proveedor, Vendedor, Comprador, Producto, Pedido, Postulacion
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
    postulaciones = Postulacion.objects.filter(producto__proveedor=proveedor).order_by('-fecha')
    
    contexto = {
        'proveedor': proveedor,
        'productos': productos,
        'pedidos': pedidos,
        'postulaciones': postulaciones,
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
    
    # Obtener todos los productos de empresas/proveedores disponibles para postular
    productos_disponibles = Producto.objects.filter(proveedor__isnull=False)
    postulaciones_dict = {p.producto_id: p for p in Postulacion.objects.filter(vendedor=vendedor)}
    for prod in productos_disponibles:
        prod.postulacion = postulaciones_dict.get(prod.id)
        
    contexto = {
        'vendedor': vendedor,
        'productos': productos,
        'pedidos': pedidos,
        'productos_disponibles': productos_disponibles,
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
    
    # Obtener todas las empresas/proveedores que tienen productos
    proveedores = Proveedor.objects.filter(productos__isnull=False).distinct().prefetch_related('productos')
    # También productos que no tengan proveedor
    productos_sin_proveedor = Producto.objects.filter(proveedor__isnull=True)
    
    contexto = {
        'comprador': comprador,
        'proveedores': proveedores,
        'productos_sin_proveedor': productos_sin_proveedor,
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
    if role != 'proveedor' or not role_id:
        messages.error(request, "Acceso denegado. Solo las empresas/proveedores pueden registrar productos.")
        return redirect('index')
        
    if request.method == 'POST':
        formulario = ProductoForm(request.POST)
        if formulario.is_valid():
            producto = formulario.save(commit=False)
            producto.proveedor = Proveedor.objects.get(pk=role_id)
            producto.save()
            messages.success(request, f"Producto '{producto.nombre}' registrado con éxito.")
            return redirect('index')
    else:
        formulario = ProductoForm(initial={'proveedor': role_id})
        
    return render(request, 'crear_producto.html', {'formulario': formulario})

def editar_producto(request, id):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'proveedor' or not role_id:
        messages.error(request, "Acceso denegado. Solo las empresas/proveedores pueden editar productos.")
        return redirect('index')
        
    producto = get_object_or_404(Producto, pk=id)
    if producto.proveedor_id != role_id:
        messages.error(request, "Acceso denegado. Este producto no te pertenece.")
        return redirect('index')

    if request.method == 'POST':
        formulario = ProductoForm(request.POST, instance=producto)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, f"Producto '{producto.nombre}' actualizado.")
            return redirect('index')
    else:
        formulario = ProductoForm(instance=producto)
    return render(request, 'editar_producto.html', {'formulario': formulario})

def eliminar_producto(request, id):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'proveedor' or not role_id:
        messages.error(request, "Acceso denegado. Solo las empresas/proveedores pueden eliminar productos.")
        return redirect('index')
        
    producto = get_object_or_404(Producto, pk=id)
    if producto.proveedor_id != role_id:
        messages.error(request, "Acceso denegado. Este producto no te pertenece.")
        return redirect('index')

    producto.delete()
    messages.success(request, f"Producto {producto.nombre} eliminado.")
    return redirect('index')

# Pedidos / Flujos de Transacción — con pasarela de pagos y código de entrega
def comprar_producto(request, id):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'comprador' or not role_id:
        return redirect('index')
        
    comprador = get_object_or_404(Comprador, pk=role_id)
    producto = get_object_or_404(Producto, pk=id)
    
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except (ValueError, TypeError):
            cantidad = 1

        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser mayor que 0.")
            return redirect('dashboard_comprador')

        # Obtener datos de la pasarela de pagos
        porcentaje_pago = int(request.POST.get('porcentaje_pago', 100))
        metodo_pago = request.POST.get('metodo_pago', 'tarjeta_credito')

        # Validar porcentaje
        if porcentaje_pago not in [50, 100]:
            porcentaje_pago = 100

        # Validar método de pago
        metodos_validos = ['tarjeta_credito', 'tarjeta_debito', 'transferencia']
        if metodo_pago not in metodos_validos:
            metodo_pago = 'tarjeta_credito'

        # Verificar si hay suficiente stock
        if producto.cantidad >= cantidad:
            producto.cantidad -= cantidad
            producto.save()
            
            # Calcular montos
            total = Decimal(str(cantidad)) * producto.precio
            monto_pagado = total * Decimal(str(porcentaje_pago)) / Decimal('100')
            monto_pendiente = total - monto_pagado
            pago_completado = (porcentaje_pago == 100)
            
            # Generar código de entrega único
            codigo_entrega = Pedido.generar_codigo()
            
            # Crear el Pedido con datos de pago y código de entrega
            Pedido.objects.create(
                comprador=comprador,
                producto=producto,
                cantidad=cantidad,
                estado='Pendiente',
                porcentaje_pago=porcentaje_pago,
                metodo_pago=metodo_pago,
                monto_pagado=monto_pagado,
                monto_pendiente=monto_pendiente,
                pago_completado=pago_completado,
                codigo_entrega=codigo_entrega,
            )
            
            # Mensajes informativos
            metodo_display = dict(Pedido.METODO_PAGO_CHOICES).get(metodo_pago, metodo_pago)
            msg = f"✅ Pedido realizado para {cantidad} unidad(es) de {producto.nombre}. "
            msg += f"Método: {metodo_display}. "
            if pago_completado:
                msg += f"Pago completo: ${monto_pagado}. "
            else:
                msg += f"Pago parcial (50%): ${monto_pagado}. Pendiente: ${monto_pendiente}. "
            msg += f"🔐 Tu código de entrega es: {codigo_entrega}"
            messages.success(request, msg)
        else:
            messages.error(request, f"No hay suficiente stock para {producto.nombre}. Stock disponible: {producto.cantidad}")
    else:
        messages.error(request, "Método no permitido.")
        
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


# ========== SISTEMA DE ENTREGA SEGURA ==========

def confirmar_entrega(request, id):
    """El vendedor ingresa el código de entrega para confirmar que el pedido
    fue entregado al tendero correcto."""
    role = request.session.get('role')
    if role not in ['vendedor', 'proveedor']:
        messages.error(request, "Solo los vendedores o proveedores pueden confirmar entregas.")
        return redirect('index')
    
    pedido = get_object_or_404(Pedido, pk=id)
    
    if pedido.entrega_confirmada:
        messages.info(request, f"La entrega del pedido #{pedido.id} ya fue confirmada anteriormente.")
        return redirect('index')
    
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip().upper()
        
        if not codigo_ingresado:
            messages.error(request, "Debes ingresar el código de entrega.")
            return redirect('index')
        
        if codigo_ingresado == pedido.codigo_entrega:
            # ¡Código correcto! Confirmar entrega
            pedido.entrega_confirmada = True
            pedido.fecha_entrega = timezone.now()
            pedido.estado = 'Recibido'
            pedido.save()
            
            if pedido.pago_completado:
                messages.success(request, 
                    f"✅ Entrega verificada para pedido #{pedido.id}. "
                    f"Pago COMPLETO al 100% — ${pedido.monto_pagado}. "
                    f"¡Transacción finalizada!"
                )
            else:
                messages.success(request,
                    f"✅ Entrega verificada para pedido #{pedido.id}. "
                    f"⚠️ Pago PARCIAL (50%) — Pagado: ${pedido.monto_pagado}. "
                    f"Pendiente por cobrar: ${pedido.monto_pendiente}."
                )
        else:
            messages.error(request,
                f"❌ Código de entrega incorrecto para pedido #{pedido.id}. "
                f"Verifica el código con el tendero/comprador e intenta nuevamente."
            )
    
    return redirect('index')


def completar_pago(request, id):
    """El comprador paga el 50% restante de un pedido con pago parcial."""
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'comprador' or not role_id:
        return redirect('index')
    
    pedido = get_object_or_404(Pedido, pk=id)
    
    # Validar que pertenezca al comprador activo
    if pedido.comprador.id != role_id:
        messages.error(request, "Acceso no autorizado a este pedido.")
        return redirect('index')
    
    if pedido.pago_completado:
        messages.info(request, f"El pedido #{pedido.id} ya está pagado al 100%.")
        return redirect('dashboard_comprador')
    
    if request.method == 'POST':
        # Completar el pago
        pedido.monto_pagado = pedido.monto_pagado + pedido.monto_pendiente
        pedido.monto_pendiente = Decimal('0.00')
        pedido.pago_completado = True
        pedido.save()
        
        messages.success(request, 
            f"✅ Pago completado exitosamente para pedido #{pedido.id}. "
            f"Total pagado: ${pedido.monto_pagado}. ¡Pago al 100%!"
        )
    
    return redirect('dashboard_comprador')


def postular_producto(request, id):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'vendedor' or not role_id:
        messages.error(request, "Solo los vendedores pueden postularse.")
        return redirect('index')
        
    vendedor = get_object_or_404(Vendedor, pk=role_id)
    producto = get_object_or_404(Producto, pk=id)
    
    if not producto.proveedor:
        messages.error(request, "Este producto no tiene un proveedor asociado.")
        return redirect('dashboard_vendedor')

    postulacion, created = Postulacion.objects.get_or_create(
        vendedor=vendedor,
        producto=producto,
        defaults={'estado': 'Pendiente'}
    )
    
    if created:
        messages.success(request, f"Te has postulado con éxito para vender '{producto.nombre}'. Esperando aprobación.")
    else:
        if postulacion.estado == 'Rechazado':
            postulacion.estado = 'Pendiente'
            postulacion.save()
            messages.success(request, f"Has reenviado tu postulación para '{producto.nombre}'.")
        else:
            messages.info(request, f"Ya tienes una postulación en estado '{postulacion.estado}' para este producto.")
            
    return redirect('dashboard_vendedor')


def aprobar_postulacion(request, id):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'proveedor' or not role_id:
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
        
    postulacion = get_object_or_404(Postulacion, pk=id)
    if postulacion.producto.proveedor_id != role_id:
        messages.error(request, "Este producto no te pertenece.")
        return redirect('dashboard_proveedor')
        
    postulacion.estado = 'Aprobado'
    postulacion.save()
    
    producto = postulacion.producto
    producto.vendedor = postulacion.vendedor
    producto.save()
    
    # Rechazar otras pendientes
    Postulacion.objects.filter(producto=producto, estado='Pendiente').exclude(id=postulacion.id).update(estado='Rechazado')
    
    messages.success(request, f"Postulación aprobada. {postulacion.vendedor.nombre} ahora es el vendedor de '{producto.nombre}'.")
    return redirect('dashboard_proveedor')


def rechazar_postulacion(request, id):
    role = request.session.get('role')
    role_id = request.session.get('role_id')
    if role != 'proveedor' or not role_id:
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
        
    postulacion = get_object_or_404(Postulacion, pk=id)
    if postulacion.producto.proveedor_id != role_id:
        messages.error(request, "Este producto no te pertenece.")
        return redirect('dashboard_proveedor')
        
    postulacion.estado = 'Rechazado'
    postulacion.save()
    
    messages.info(request, f"Postulación de {postulacion.vendedor.nombre} rechazada.")
    return redirect('dashboard_proveedor')
