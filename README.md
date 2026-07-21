# Proyecto Bimestral - ISBEN

Este es el repositorio del proyecto bimestral basado en Django.

## Requisitos Previos

Para ejecutar el proyecto de forma correcta sin afectar tu entorno global, es recomendable usar un entorno virtual. Necesitarás tener instalado:

- **Python 3.8+** (Recomendado)

## Pasos para la Instalación y Ejecución

Sigue estos comandos paso a paso desde la carpeta raíz del proyecto (`Proyecto-Bimestral`):

1. **Crear un entorno virtual**
   Esto creará una carpeta llamada `venv` donde se instalarán las dependencias del proyecto.
   ```bash
   python -m venv venv
   ```

2. **Activar el entorno virtual**
   - **En Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **En macOS o Linux:**
     ```bash
     source venv/bin/activate
     ```

3. **Instalar las dependencias**
   Con el entorno virtual activado, instala Django y otras librerías necesarias con el archivo de requerimientos:
   ```bash
   pip install -r requirements.txt
   ```

4. **Navegar a la carpeta del proyecto Django**
   El código ejecutable de Django (donde se encuentra `manage.py`) está dentro de `proyectoISBEN/ISBEN`.
   ```bash
   cd proyectoISBEN/ISBEN
   ```

5. **Aplicar las migraciones (Opcional, pero recomendado)**
   Aunque la base de datos `db.sqlite3` ya existe y tiene datos iniciales, es buena práctica confirmar que está al día:
   ```bash
   python manage.py migrate
   ```

6. **Levantar el servidor local**
   ```bash
   python manage.py runserver
   ```
   Una vez ejecutado este comando, podrás acceder al proyecto desde tu navegador en la dirección: **http://127.0.0.1:8000/**

---

## Usuarios y Contraseñas del Sistema

La base de datos actual cuenta con los siguientes usuarios con privilegios de **Administrador (Superuser)**:

- **Usuario 1:** `admin`
- **Usuario 2:** `admin1`

*(Las contraseñas de estos usuarios corresponden a las que se configuraron al momento de crearlos. Si eres ajeno al proyecto y no conoces dichas contraseñas, puedes seguir los pasos a continuación para crear un nuevo administrador).*

### Usuarios de Prueba (Roles)

Para poder testear las distintas funcionalidades de la aplicación, ya existen usuarios registrados en la base de datos para cada rol. *(Nota: Las contraseñas son las que se definieron al momento de crearlos en el sistema)*:

**Proveedores:**
- `cocacola` `CocaCola123`
- `pepsico` `PepsiCo123`
- `nestle` `Nestle123`

**Vendedores:**
- `carlos_bueno` `VendedorGood1`
- `juan_malo` `VendedorBad1`

**Compradores (Tenderos):**
- `don_pepe` `DonPepe123`

### ¿Cómo crear un nuevo usuario Administrador?

Si necesitas ingresar al panel de administración (en `http://127.0.0.1:8000/admin/`) y no conoces la contraseña de los usuarios mencionados arriba, puedes crear fácilmente un nuevo superusuario. 

Con el entorno virtual activado y dentro de la carpeta donde se encuentra `manage.py` (`proyectoISBEN/ISBEN`), ejecuta:

```bash
python manage.py createsuperuser
```
Luego, la terminal te pedirá que ingreses un nombre de usuario, un correo electrónico (opcional) y una contraseña (la cual no se mostrará en pantalla mientras la escribes). Con esto, podrás acceder sin problemas.
