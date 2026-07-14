import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ISBEN.settings")
django.setup()

from django.contrib.auth.hashers import make_password
from proyecto.models import Vendedor, Comprador, Proveedor, Producto

def seed():
    print("--- Iniciando Seeding de Datos de Prueba ---")
    
    # 1. Proveedor Coca-Cola
    prov = Proveedor.objects.filter(usuario="cocacola").first()
    if not prov:
        prov = Proveedor.objects.filter(ruc="1790000000001").first()
        
    if prov:
        prov.nombre = "Coca-Cola"
        prov.ruc = "1790000000001"
        prov.direccion = "Av. de los Granados y Av. Eloy Alfaro, Quito"
        prov.usuario = "cocacola"
        prov.contrasenia = make_password("CocaCola123")
        prov.save()
        print("[OK] Proveedor Coca-Cola actualizado.")
    else:
        prov = Proveedor.objects.create(
            nombre="Coca-Cola",
            ruc="1790000000001",
            direccion="Av. de los Granados y Av. Eloy Alfaro, Quito",
            usuario="cocacola",
            contrasenia=make_password("CocaCola123")
        )
        print("[OK] Proveedor Coca-Cola creado.")

    # 2. Vendedor Bueno
    v_bueno = Vendedor.objects.filter(usuario="carlos_bueno").first()
    if not v_bueno:
        v_bueno = Vendedor.objects.filter(cedula="1725555551").first()
        
    if v_bueno:
        v_bueno.nombre = "Carlos Pérez (Vendedor Bueno)"
        v_bueno.cedula = "1725555551"
        v_bueno.telefono = "0987654321"
        v_bueno.usuario = "carlos_bueno"
        v_bueno.contrasenia = make_password("VendedorGood1")
        v_bueno.reputacion = "Excelente"
        v_bueno.calificacion = 4.90
        v_bueno.descripcion_perfil = "Vendedor estrella con más de 5 años de experiencia en la distribución de bebidas y alimentos. Excelente trato al cliente y entregas siempre a tiempo."
        v_bueno.save()
        print("[OK] Vendedor Carlos Pérez (Bueno) actualizado.")
    else:
        v_bueno = Vendedor.objects.create(
            nombre="Carlos Pérez (Vendedor Bueno)",
            cedula="1725555551",
            telefono="0987654321",
            usuario="carlos_bueno",
            contrasenia=make_password("VendedorGood1"),
            reputacion="Excelente",
            calificacion=4.90,
            descripcion_perfil="Vendedor estrella con más de 5 años de experiencia en la distribución de bebidas y alimentos. Excelente trato al cliente y entregas siempre a tiempo."
        )
        print("[OK] Vendedor Carlos Pérez (Bueno) creado.")

    # 3. Vendedor Malo
    v_malo = Vendedor.objects.filter(usuario="juan_malo").first()
    if not v_malo:
        v_malo = Vendedor.objects.filter(cedula="1725555552").first()
        
    if v_malo:
        v_malo.nombre = "Juan Rodríguez (Vendedor Malo)"
        v_malo.cedula = "1725555552"
        v_malo.telefono = "0987654322"
        v_malo.usuario = "juan_malo"
        v_malo.contrasenia = make_password("VendedorBad1")
        v_malo.reputacion = "Mala"
        v_malo.calificacion = 2.10
        v_malo.descripcion_perfil = "Vendedor con historial de retrasos en las entregas, quejas de clientes por pedidos incompletos y falta de comunicación."
        v_malo.save()
        print("[OK] Vendedor Juan Rodríguez (Malo) actualizado.")
    else:
        v_malo = Vendedor.objects.create(
            nombre="Juan Rodríguez (Vendedor Malo)",
            cedula="1725555552",
            telefono="0987654322",
            usuario="juan_malo",
            contrasenia=make_password("VendedorBad1"),
            reputacion="Mala",
            calificacion=2.10,
            descripcion_perfil="Vendedor con historial de retrasos en las entregas, quejas de clientes por pedidos incompletos y falta de comunicación."
        )
        print("[OK] Vendedor Juan Rodríguez (Malo) creado.")

    # 4. Comprador / Tendero
    comp = Comprador.objects.filter(usuario="don_pepe").first()
    if not comp:
        comp = Comprador.objects.filter(cedula="1725555553").first()
        
    if comp:
        comp.nombre = "Tienda Don Pepe (Tendero)"
        comp.cedula = "1725555553"
        comp.usuario = "don_pepe"
        comp.contrasenia = make_password("DonPepe123")
        comp.direccion = "Barrio La Floresta, Calle Lérida"
        comp.save()
        print("[OK] Comprador Tienda Don Pepe actualizado.")
    else:
        comp = Comprador.objects.create(
            nombre="Tienda Don Pepe (Tendero)",
            cedula="1725555553",
            usuario="don_pepe",
            contrasenia=make_password("DonPepe123"),
            direccion="Barrio La Floresta, Calle Lérida"
        )
        print("[OK] Comprador Tienda Don Pepe creado.")

    # 5. Agregar productos para Coca-Cola
    productos = [
        {"nombre": "Coca-Cola Sabor Original 1.5L", "descripcion": "Bebida gaseosa refrescante sabor original de 1.5 litros.", "cantidad": 100, "precio": 1.80},
        {"nombre": "Coca-Cola Sin Azúcar 1.5L", "descripcion": "Bebida gaseosa refrescante sin calorías sabor original de 1.5 litros.", "cantidad": 80, "precio": 1.70},
        {"nombre": "Sprite Limón-Lime 1.5L", "descripcion": "Bebida carbonatada refrescante sabor limón-lima de 1.5 litros.", "cantidad": 50, "precio": 1.60},
        {"nombre": "Fanta Naranja 1.5L", "descripcion": "Bebida gaseosa refrescante sabor naranja de 1.5 litros.", "cantidad": 60, "precio": 1.60},
    ]

    for prod_info in productos:
        prod = Producto.objects.filter(nombre=prod_info["nombre"], proveedor=prov).first()
        if prod:
            prod.descripcion = prod_info["descripcion"]
            prod.cantidad = prod_info["cantidad"]
            prod.precio = prod_info["precio"]
            prod.save()
            print(f"[OK] Producto '{prod.nombre}' actualizado.")
        else:
            prod = Producto.objects.create(
                nombre=prod_info["nombre"],
                proveedor=prov,
                descripcion=prod_info["descripcion"],
                cantidad=prod_info["cantidad"],
                precio=prod_info["precio"]
            )
            print(f"[OK] Producto '{prod.nombre}' creado.")
            
    print("--- Seeding completado con éxito ---")

if __name__ == "__main__":
    seed()
