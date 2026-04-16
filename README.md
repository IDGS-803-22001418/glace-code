# Maison Code

## 📋 Descripción

**Maison Code** es una aplicación web desarrollada en **Flask** diseñada para la empresa Maison Glace, dedicada a la producción y distribución de postres. La aplicación proporciona un sistema integral de gestión que cubre desde la administración de insumos hasta la venta final de productos.

### Características Principales

La aplicación incluye los siguientes módulos:

- **👥 Usuarios** - Gestión de permisos y acceso de usuarios
- **📦 Insumos** - Control de materias primas e ingredientes
- **🍰 Productos** - Catálogo de productos terminados
- **🛒 Punto de Venta** - Sistema de ventas en mostrador
- **📲 Pedidos Online** - Gestión de pedidos a través de plataforma web
- **👨‍💼 Clientes** - Base de datos de clientes
- **🏭 Producción** - Planificación y control de procesos de fabricación
- **🚚 Proveedores** - Gestión de relaciones con proveedores
- **📊 Reportes** - Generación de reportes y análisis
- **🗑️ Mermas** - Control de pérdidas y desperdicio
- **💳 Compras** - Gestión de órdenes de compra
- **⚙️ Configuración del Sistema** - Parámetros generales de la aplicación

---

## �️ Modelo de Base de Datos

A continuación se presenta el diagrama entidad-relación de la base de datos utilizada por la aplicación:

```mermaid
erDiagram
    User {
        int id PK
        string nombre_completo
        string correo_electronico
        string password
        string rol_asignado
        boolean is_active
    }
    Customer {
        int id PK
        int user_id FK
        string telefono
        string direccion_despacho
        int puntos_acumulados
        boolean is_active
    }
    UnidadMedida {
        int id PK
        string nombre
        string abreviatura
    }
    Insumo {
        int id PK
        string nombre_insumo
        string categoria
        float stock_actual
        float stock_minimo_alerta
        boolean is_active
        int unidad_base_id FK
    }
    ConversionUnidad {
        int id PK
        float factor_conversion
        int insumo_id FK
        int unidad_destino_id FK
        boolean is_active
    }
    Product {
        int id PK
        string nombre_producto
        string categoria
        float precio_venta
        int stock
        int pedido_minimo
        string imagen_url
        string descripcion
        boolean is_active
    }
    Recipe {
        int id PK
        int product_id FK
        string nombre_variante
        float cantidad_producida
        int tiempo_estimado_min
        boolean is_active
    }
    RecipeDetail {
        int recipe_id PK
        int insumo_id PK
        float cantidad
        int unidad_medida_id FK
        boolean is_active
    }
    Merma {
        int id PK
        int insumo_id FK
        int producto_id FK
        float cantidad_perdida
        string causa
        text notas_adicionales
        datetime fecha_registro
        boolean is_active
    }
    ProductionTask {
        int id PK
        int receta_id FK
        string estado
        string prioridad
        datetime fecha_limite
        datetime fecha_creacion
        boolean is_active
    }
    Venta {
        int id PK
        int cliente_id FK
        datetime fecha_hora
        string metodo_pago
        float monto_recibido
        float monto_cambio
        string lugar_entrega
        datetime fecha_hora_entrega
        string estado
    }
    DetalleVenta {
        int id PK
        int venta_id FK
        int producto_id FK
        int cantidad
        float precio_unitario_aplicado
    }
    CustomOrder {
        int id PK
        int detalle_venta_id FK
        string tipo_evento
        text instrucciones_decoracion
    }
    Supplier {
        int id PK
        string nombre_empresa
        string categoria_insumos
        string nombre_contacto
        string telefono
        string correo_electronico
        string direccion_fisica
        text notas_adicionales
        boolean is_active
    }
    Purchase {
        int id PK
        int supplier_id FK
        datetime fecha_orden
        boolean is_active
    }
    PurchaseDetail {
        int id PK
        int purchase_id FK
        int insumo_id FK
        float cantidad
        float precio_unitario
        int unidad_medida_id FK
    }
    User ||--o| Customer : "has"
    Insumo ||--o{ ConversionUnidad : "has conversions"
    Product ||--o{ Recipe : "has recipes"
    Recipe ||--o{ RecipeDetail : "has details"
    RecipeDetail }o--|| Insumo : "uses"
    RecipeDetail }o--|| UnidadMedida : "measured in"
    Merma }o--|| Insumo : "affects"
    Merma }o--|| Product : "affects"
    ProductionTask }o--|| Recipe : "for"
    Venta }o--|| Customer : "by"
    Venta ||--o{ DetalleVenta : "has"
    DetalleVenta }o--|| Product : "sells"
    DetalleVenta ||--o| CustomOrder : "has"
    Supplier ||--o{ Purchase : "supplies"
    Purchase ||--o{ PurchaseDetail : "has"
    PurchaseDetail }o--|| Insumo : "buys"
    PurchaseDetail }o--|| UnidadMedida : "measured in"
    ConversionUnidad }o--|| UnidadMedida : "to"
    Insumo }o--|| UnidadMedida : "base unit"
```

---

## �🚀 Instalación y Ejecución

### Requisitos Previos

- Python 3.10 o superior
- Git
- pip (gestor de paquetes de Python)
- Node.js y npm

### Pasos de Instalación

1. **Clonar el repositorio desde GitHub:**
   ```bash
   git clone https://github.com/IDGS-803-22001418/glace-code
   ```

2. **Acceder a la carpeta del proyecto:**
   ```bash
   cd glace-code
   ```

3. **Crear un entorno virtual:**
   ```bash
   python -m venv .venv
   ```

4. **Activar el entorno virtual:**
   - En Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - En Windows:
     ```bash
     .venv\Scripts\activate
     ```

5. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Instalar dependencias de frontend:**
   ```bash
   npm install
   ```

7. **Compilar estilos con Tailwind CSS:**
   ```bash
   npx @tailwindcss/cli -i ./app/static/src/input.css -o ./app/static/dist/output.css
   ```

8. **Ejecutar migraciones de base de datos:**
   ```bash
   flask db upgrade
   ```

9. **Ejecutar la aplicación:**
   ```bash
   python run.py
   ```

   La aplicación estará disponible en `http://localhost:5000`

---

## 👨‍💻 Para Desarrolladores

### Estructura del Proyecto

```
maison-code/
├── app/                               # Código principal de la aplicación
│   ├── __init__.py                    # Inicialización de Flask
│   ├── decorators.py                  # Decoradores personalizados
│   ├── models.py                      # Modelos de base de datos
│   ├── routes/                        # Rutas
│   ├── static/                        # Archivos estáticos
│   └── templates/                     # Plantillas HTML
├── migrations/                        # Migraciones de Flask-Migrate/Alembic
├── tests/                             # Pruebas
├── config.py                          # Configuración de la aplicación
├── run.py                             # Punto de entrada de la aplicación
├── requirements.txt                   # Dependencias de Python
├── package.json                       # Dependencias/scripts de frontend
├── package-lock.json                  # Lockfile de npm
└── README.md                          # Este archivo
```

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (si es necesario) con las siguientes variables:

```
# Ejemplo de configuración
FLASK_ENV=development
SECRET_KEY=supersecretkey
DATABASE_URL=<tu_url_de_base_de_datos>
```

---

## 📝 Notas Adicionales

- Asegúrate de tener activado el entorno virtual antes de instalar dependencias o ejecutar la aplicación
- Si realizas cambios en los estilos, vuelve a ejecutar el comando de Tailwind para regenerar `app/static/dist/output.css`
- Para detener la aplicación, presiona `Ctrl + C` en la terminal
- Consulta la documentación de Flask para más información: https://flask.palletsprojects.com/

---

## Respaldos y restauraciones

```sh
mysqldump -u backups_glace_code -p glace_code --databases --set-gtid-purged=OFF > ~/backup.sql
mysql -u backups_glace_code -p < ~/backup.sql
```