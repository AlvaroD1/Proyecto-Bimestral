from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from decimal import Decimal
from .models import (
    Proveedor, Vendedor, Comprador, Producto, Pedido, Postulacion,
    InventarioTienda, ListaReposicion, ItemReposicion
)
from .forms import ProveedorForm, VendedorForm, CompradorForm, ProductoForm

def index(request):
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
            if 'roles' not in request.session:
                request.session['roles'] = {}
            roles = dict(request.session['roles'])
            roles[role] = user_obj.id
            roles[f'{role}_name'] = user_obj.nombre
            request.session['roles'] = roles

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
    request.session.pop('roles', None)
    role = request.session.pop('role', None)
    request.session.pop('role_id', None)
    request.session.pop('role_name', None)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('index')


def dashboard_proveedor(request):
    roles = request.session.get('roles', {})
    role_id = roles.get('proveedor')
    if not role_id:
        return redirect('index')
    
    proveedor = get_object_or_404(Proveedor, pk=role_id)
    # Hacerle preguntas al modelo directamente para obtener info
    productos = proveedor.obtener_productos()
    pedidos = proveedor.obtener_pedidos()
    postulaciones = Postulacion.objects.filter(producto__proveedor=proveedor).order_by('-fecha')

    # Listas de reposición recibidas de tenderos para productos de este proveedor
    listas_reposicion_recibidas = ListaReposicion.objects.filter(
        estado='Enviada',
        items__producto__proveedor=proveedor
    ).distinct().prefetch_related('items__producto', 'comprador').order_by('-fecha_envio')[:10]
    
    contexto = {
        'proveedor': proveedor,
        'productos': productos,
        'pedidos': pedidos,
        'postulaciones': postulaciones,
        'listas_reposicion_recibidas': listas_reposicion_recibidas,
        'current_role': 'proveedor',
        'current_role_name': proveedor.nombre,
    }
    return render(request, 'dashboard_proveedor.html', contexto)

def dashboard_vendedor(request):
    roles = request.session.get('roles', {})
    role_id = roles.get('vendedor')
    if not role_id:
        return redirect('index')
    
    vendedor = get_object_or_404(Vendedor, pk=role_id)
    # Hacerle preguntas al modelo directamente para obtener info
    productos = vendedor.obtener_productos()
    pedidos = vendedor.obtener_pedidos()
    
    # Obtener todas las empresas/proveedores que tienen productos
    proveedores = Proveedor.objects.filter(productos__isnull=False).distinct().prefetch_related('productos')
    
    # Obtener postulaciones del vendedor
    postulaciones_dict = {p.producto_id: p for p in Postulacion.objects.filter(vendedor=vendedor)}
    
    # Adjuntar la postulación a cada producto de cada proveedor
    for prov in proveedores:
        for prod in prov.productos.all():
            prod.postulacion = postulaciones_dict.get(prod.id)
            
    # Productos sin proveedor (si los hay)
    productos_sin_proveedor = Producto.objects.filter(proveedor__isnull=True)
    for prod in productos_sin_proveedor:
        prod.postulacion = postulaciones_dict.get(prod.id)

    # Obtener peticiones urgentes de empresas (productos esperando vendedor)
    peticiones_urgentes = Producto.objects.filter(
        solicitud_vendedor_activa=True,
        vendedor__isnull=True
    ).exclude(
        postulaciones__vendedor=vendedor
    ).distinct()
        
    contexto = {
        'vendedor': vendedor,
        'productos': productos,
        'pedidos': pedidos,
        'proveedores': proveedores,
        'productos_sin_proveedor': productos_sin_proveedor,
        'peticiones_urgentes': peticiones_urgentes,
        'current_role': 'vendedor',
        'current_role_name': vendedor.nombre,
    }
    return render(request, 'dashboard_vendedor.html', contexto)

def dashboard_comprador(request):
    roles = request.session.get('roles', {})
    role_id = roles.get('comprador')
    if not role_id:
        return redirect('index')
    
    comprador = get_object_or_404(Comprador, pk=role_id)
    # Hacerle preguntas al modelo directamente para obtener info
    pedidos = comprador.obtener_pedidos()
    
    # Obtener todas las empresas/proveedores que tienen productos
    proveedores = Proveedor.objects.filter(productos__isnull=False).distinct().prefetch_related('productos')
    # También productos que no tengan proveedor
    productos_sin_proveedor = Producto.objects.filter(proveedor__isnull=True)

    # ========== INVENTARIO DE MI TIENDA ==========
    inventario = InventarioTienda.objects.filter(
        comprador=comprador
    ).select_related('producto', 'producto__proveedor').order_by('producto__nombre')
    
    # Productos con stock bajo en la tienda del tendero
    inventario_stock_bajo = [inv for inv in inventario if inv.stock_bajo()]

    # Lista de reposición activa (borrador) del tendero
    lista_reposicion_activa = ListaReposicion.objects.filter(
        comprador=comprador, estado='Borrador'
    ).prefetch_related('items__producto__proveedor').first()

    # Listas enviadas recientes (últimas 5)
    listas_enviadas = ListaReposicion.objects.filter(
        comprador=comprador, estado='Enviada'
    ).prefetch_related('items__producto__proveedor')[:5]
    
    contexto = {
        'comprador': comprador,
        'proveedores': proveedores,
        'productos_sin_proveedor': productos_sin_proveedor,
        'pedidos': pedidos,
        'total_gastado': comprador.obtener_total_gastado(),
        'inventario': inventario,
        'inventario_stock_bajo': inventario_stock_bajo,
        'lista_reposicion_activa': lista_reposicion_activa,
        'listas_enviadas': listas_enviadas,
        'current_role': 'comprador',
        'current_role_name': comprador.nombre,
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
    roles = request.session.get('roles', {})
    role_id = roles.get('proveedor')
    if not role_id:
        messages.error(request, "Acceso denegado. Solo las empresas/proveedores pueden registrar productos.")
        return redirect('index')
        
    if request.method == 'POST':
        formulario = ProductoForm(request.POST)
        if formulario.is_valid():
            producto = formulario.save(commit=False)
            producto.proveedor = Proveedor.objects.get(pk=role_id)
            producto.save()
            messages.success(request, f"Producto '{producto.nombre}' registrado con éxito.")
            return redirect('dashboard_proveedor')
    else:
        formulario = ProductoForm(initial={'proveedor': role_id})
        
    return render(request, 'crear_producto.html', {'formulario': formulario})

def editar_producto(request, id):
    roles = request.session.get('roles', {})
    role_id = roles.get('proveedor')
    if not role_id:
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
            return redirect('dashboard_proveedor')
    else:
        formulario = ProductoForm(instance=producto)
    return render(request, 'editar_producto.html', {'formulario': formulario})

def eliminar_producto(request, id):
    roles = request.session.get('roles', {})
    role_id = roles.get('proveedor')
    if not role_id:
        messages.error(request, "Acceso denegado. Solo las empresas/proveedores pueden eliminar productos.")
        return redirect('index')
        
    producto = get_object_or_404(Producto, pk=id)
    if producto.proveedor_id != role_id:
        messages.error(request, "Acceso denegado. Este producto no te pertenece.")
        return redirect('index')

    producto.delete()
    messages.success(request, f"Producto {producto.nombre} eliminado.")
    return redirect('dashboard_proveedor')

# Pedidos / Flujos de Transacción — con pasarela de pagos y código de entrega
def comprar_producto(request, id):
    roles = request.session.get('roles', {})
    role_id = roles.get('comprador')
    if not role_id:
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
    roles = request.session.get('roles', {})
    if 'proveedor' not in roles and 'vendedor' not in roles:
        return redirect('index')
        
    pedido = get_object_or_404(Pedido, pk=id)
    if pedido.estado == 'Pendiente':
        pedido.estado = 'Enviado'
        pedido.save()
        messages.success(request, f"El pedido #{pedido.id} ha sido despachado / enviado.")
    else:
        messages.error(request, f"El pedido #{pedido.id} no se puede enviar porque está en estado {pedido.estado}.")
        
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    if 'proveedor' in roles:
        return redirect('dashboard_proveedor')
    return redirect('dashboard_vendedor')

def recibir_pedido(request, id):
    roles = request.session.get('roles', {})
    role_id = roles.get('comprador')
    if not role_id:
        return redirect('index')
        
    pedido = get_object_or_404(Pedido, pk=id)
    # Validar que pertenezca al comprador activo
    if pedido.comprador.id != role_id:
        messages.error(request, "Acceso no autorizado a este pedido.")
        return redirect('index')
        
    if not pedido.entrega_confirmada:
        messages.error(request, "No puedes recibir el pedido sin antes confirmar la entrega mediante el código de seguridad.")
        return redirect('dashboard_comprador')
        
    if pedido.estado in ['Pendiente', 'Enviado']:
        pedido.estado = 'Recibido'
        pedido.save()
        
        # Auto-agregar al inventario de la tienda del tendero
        inv, created = InventarioTienda.objects.get_or_create(
            comprador=pedido.comprador,
            producto=pedido.producto,
            defaults={'cantidad': 0, 'stock_minimo': 5}
        )
        inv.cantidad += pedido.cantidad
        inv.save()
        
        messages.success(request, 
            f"Has marcado el pedido #{pedido.id} como RECIBIDO. "
            f"Se agregaron {pedido.cantidad} unidad(es) de '{pedido.producto.nombre}' a tu inventario de tienda. ¡Gracias!"
        )
    else:
        messages.error(request, f"El pedido ya está en estado {pedido.estado}.")
        
    return redirect('dashboard_comprador')


# ========== SISTEMA DE ENTREGA SEGURA ==========

def confirmar_entrega(request, id):
    """El vendedor ingresa el código de entrega para confirmar que el pedido
    fue entregado al tendero correcto."""
    roles = request.session.get('roles', {})
    if 'vendedor' not in roles and 'proveedor' not in roles:
        messages.error(request, "Solo los vendedores o proveedores pueden confirmar entregas.")
        return redirect('index')
    
    pedido = get_object_or_404(Pedido, pk=id)
    
    def get_redirect():
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        if 'vendedor' in roles:
            return redirect('dashboard_vendedor')
        return redirect('dashboard_proveedor')

    if pedido.entrega_confirmada:
        messages.info(request, f"La entrega del pedido #{pedido.id} ya fue confirmada anteriormente.")
        return get_redirect()
    
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip().upper()
        
        if not codigo_ingresado:
            messages.error(request, "Debes ingresar el código de entrega.")
            return get_redirect()
        
        if codigo_ingresado == pedido.codigo_entrega:
            # ¡Código correcto! Confirmar entrega
            pedido.entrega_confirmada = True
            pedido.fecha_entrega = timezone.now()
            if pedido.estado == 'Pendiente':
                pedido.estado = 'Enviado'
            
            pago_completado_ahora = False
            monto_cobrado = Decimal('0.00')
            
            # Registrar el cobro de la parte pendiente si es indicado
            registrar_pago = request.POST.get('cobrar_pendiente') == '1'
            if not pedido.pago_completado and registrar_pago:
                monto_cobrado = pedido.monto_pendiente
                pedido.monto_pagado += pedido.monto_pendiente
                pedido.monto_pendiente = Decimal('0.00')
                pedido.pago_completado = True
                pago_completado_ahora = True
                
            pedido.save()
            
            if pago_completado_ahora:
                messages.success(request, 
                    f"✅ Entrega y Pago Verificados para pedido #{pedido.id}. "
                    f"Se cobró y registró el 50% restante (${monto_cobrado}). ¡Pago al 100% completado!"
                )
            elif pedido.pago_completado:
                messages.success(request, 
                    f"✅ Entrega verificada para pedido #{pedido.id}. "
                    f"El pago del pedido ya está COMPLETO al 100% — ${pedido.monto_pagado}. "
                    f"¡Transacción finalizada con éxito!"
                )
            else:
                messages.success(request,
                    f"✅ Entrega verificada para pedido #{pedido.id}. "
                    f"⚠️ Pago PARCIAL (50%) — Pagado: ${pedido.monto_pagado}. "
                    f"Faltante por cobrar: ${pedido.monto_pendiente}."
                )
        else:
            messages.error(request,
                f"❌ Código de entrega incorrecto para pedido #{pedido.id}. "
                f"Verifica el código con el tendero/comprador e intenta nuevamente."
            )
    
    return get_redirect()


def completar_pago(request, id):
    """El comprador paga el 50% restante de un pedido con pago parcial."""
    roles = request.session.get('roles', {})
    role_id = roles.get('comprador')
    if not role_id:
        return redirect('index')
    
    pedido = get_object_or_404(Pedido, pk=id)
    
    # Validar que pertenezca al comprador activo
    if pedido.comprador.id != role_id:
        messages.error(request, "Acceso no autorizado a este pedido.")
        return redirect('index')
    
    if not pedido.entrega_confirmada:
        messages.error(request, "No puedes completar el pago restante porque la entrega aún no ha sido confirmada con el código de seguridad.")
        return redirect('dashboard_comprador')
    
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
    roles = request.session.get('roles', {})
    role_id = roles.get('vendedor')
    if not role_id:
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
    roles = request.session.get('roles', {})
    role_id = roles.get('proveedor')
    if not role_id:
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
    producto.solicitud_vendedor_activa = False
    producto.save()
    
    # Rechazar otras pendientes
    Postulacion.objects.filter(producto=producto, estado='Pendiente').exclude(id=postulacion.id).update(estado='Rechazado')
    
    messages.success(request, f"Postulación aprobada. {postulacion.vendedor.nombre} ahora es el vendedor de '{producto.nombre}'.")
    return redirect('dashboard_proveedor')


def rechazar_postulacion(request, id):
    roles = request.session.get('roles', {})
    role_id = roles.get('proveedor')
    if not role_id:
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


def solicitar_vendedor(request, id):
    roles = request.session.get('roles', {})
    role_id = roles.get('proveedor')
    if not role_id:
        return redirect('index')
        
    producto = get_object_or_404(Producto, pk=id)
    if producto.proveedor_id != role_id:
        messages.error(request, "Este producto no te pertenece.")
        return redirect('dashboard_proveedor')
        
    producto.solicitud_vendedor_activa = True
    producto.save()
    messages.success(request, f"Se ha enviado la petición a todos los vendedores para postularse al producto '{producto.nombre}'.")
    return redirect('dashboard_proveedor')


# ========== SISTEMA DE ALERTAS DE STOCK Y REPOSICIÓN (TENDERO/COMPRADOR) ==========

def agregar_a_reposicion(request, producto_id):
    """Agrega un producto a la lista de reposición borrador del tendero (comprador)."""
    roles = request.session.get('roles', {})
    role_id = roles.get('comprador')
    if not role_id:
        messages.error(request, "Solo los tenderos pueden gestionar listas de reposición.")
        return redirect('index')
    
    comprador = get_object_or_404(Comprador, pk=role_id)
    producto = get_object_or_404(Producto, pk=producto_id)
    
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 10))
        except (ValueError, TypeError):
            cantidad = 10
        
        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser mayor a 0.")
            return redirect('dashboard_comprador')
        
        # Obtener o crear la lista borrador activa
        lista, lista_creada = ListaReposicion.objects.get_or_create(
            comprador=comprador,
            estado='Borrador',
            defaults={'notas': ''}
        )
        
        # Verificar si el producto ya está en la lista
        item_existente = ItemReposicion.objects.filter(lista=lista, producto=producto).first()
        if item_existente:
            item_existente.cantidad_solicitada += cantidad
            item_existente.save()
            messages.success(request, 
                f"📦 Se actualizó la cantidad de '{producto.nombre}' en tu lista de reposición. "
                f"Nueva cantidad total: {item_existente.cantidad_solicitada} unidades."
            )
        else:
            ItemReposicion.objects.create(
                lista=lista,
                producto=producto,
                cantidad_solicitada=cantidad
            )
            messages.success(request, 
                f"✅ '{producto.nombre}' agregado a tu lista de reposición ({cantidad} unidades)."
            )
    
    return redirect('dashboard_comprador')


def ver_lista_reposicion(request):
    """Muestra la lista de reposición activa del tendero (comprador)."""
    roles = request.session.get('roles', {})
    role_id = roles.get('comprador')
    if not role_id:
        return redirect('index')
    
    comprador = get_object_or_404(Comprador, pk=role_id)
    
    # Lista borrador activa
    lista_activa = ListaReposicion.objects.filter(
        comprador=comprador, estado='Borrador'
    ).prefetch_related('items__producto__proveedor').first()
    
    # Historial de listas enviadas
    listas_enviadas = ListaReposicion.objects.filter(
        comprador=comprador, estado='Enviada'
    ).prefetch_related('items__producto__proveedor').order_by('-fecha_envio')[:10]
    
    # Agrupar ítems por proveedor si hay lista activa
    items_por_proveedor = None
    if lista_activa:
        items_por_proveedor = lista_activa.obtener_items_por_proveedor()
    
    contexto = {
        'comprador': comprador,
        'lista_activa': lista_activa,
        'items_por_proveedor': items_por_proveedor,
        'listas_enviadas': listas_enviadas,
        'current_role': 'comprador',
        'current_role_name': comprador.nombre,
    }
    return render(request, 'lista_reposicion.html', contexto)


def eliminar_item_reposicion(request, item_id):
    """Elimina un ítem de la lista de reposición borrador."""
    roles = request.session.get('roles', {})
    role_id = roles.get('comprador')
    if not role_id:
        return redirect('index')
    
    item = get_object_or_404(ItemReposicion, pk=item_id)
    
    # Verificar que la lista pertenece al comprador y está en borrador
    if item.lista.comprador_id != role_id or item.lista.estado != 'Borrador':
        messages.error(request, "No puedes modificar esta lista.")
        return redirect('dashboard_comprador')
    
    nombre_producto = item.producto.nombre
    lista = item.lista
    item.delete()
    
    # Si la lista quedó vacía, eliminarla
    if lista.items.count() == 0:
        lista.delete()
        messages.info(request, f"Se eliminó '{nombre_producto}' y la lista quedó vacía, por lo que fue eliminada.")
    else:
        messages.success(request, f"Se eliminó '{nombre_producto}' de la lista de reposición.")
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('dashboard_comprador')


def enviar_lista_reposicion(request, lista_id):
    """Envía la lista de reposición (cambia estado a 'Enviada')."""
    roles = request.session.get('roles', {})
    role_id = roles.get('comprador')
    if not role_id:
        return redirect('index')
    
    lista = get_object_or_404(ListaReposicion, pk=lista_id)
    
    if lista.comprador_id != role_id:
        messages.error(request, "No puedes enviar esta lista.")
        return redirect('dashboard_comprador')
    
    if lista.estado != 'Borrador':
        messages.info(request, "Esta lista ya fue enviada.")
        return redirect('dashboard_comprador')
    
    if lista.items.count() == 0:
        messages.error(request, "No puedes enviar una lista vacía.")
        return redirect('dashboard_comprador')
    
    # Guardar notas si se enviaron
    if request.method == 'POST':
        notas = request.POST.get('notas', '').strip()
        if notas:
            lista.notas = notas
    
    lista.estado = 'Enviada'
    lista.fecha_envio = timezone.now()
    lista.save()
    
    # Generar resumen para el mensaje
    total_items = lista.items.count()
    total_unidades = sum(item.cantidad_solicitada for item in lista.items.all())
    
    messages.success(request, 
        f"📨 Lista de reposición enviada con éxito. "
        f"{total_items} producto(s), {total_unidades} unidades totales solicitadas. "
        f"Los proveedores podrán verla en su panel de control."
    )
    
    return redirect('dashboard_comprador')


def actualizar_inventario(request, inventario_id):
    """Permite al tendero actualizar la cantidad de un producto en su inventario."""
    roles = request.session.get('roles', {})
    role_id = roles.get('comprador')
    if not role_id:
        return redirect('index')
    
    inv = get_object_or_404(InventarioTienda, pk=inventario_id)
    
    if inv.comprador_id != role_id:
        messages.error(request, "No puedes modificar este inventario.")
        return redirect('dashboard_comprador')
    
    if request.method == 'POST':
        try:
            nueva_cantidad = int(request.POST.get('cantidad', inv.cantidad))
        except (ValueError, TypeError):
            nueva_cantidad = inv.cantidad
        
        if nueva_cantidad < 0:
            nueva_cantidad = 0
        
        inv.cantidad = nueva_cantidad
        
        # Actualizar stock mínimo si se envió
        try:
            nuevo_minimo = int(request.POST.get('stock_minimo', inv.stock_minimo))
            if nuevo_minimo >= 0:
                inv.stock_minimo = nuevo_minimo
        except (ValueError, TypeError):
            pass
        
        inv.save()
        messages.success(request, f"📦 Inventario de '{inv.producto.nombre}' actualizado a {inv.cantidad} unidades.")
    
    return redirect('dashboard_comprador')

