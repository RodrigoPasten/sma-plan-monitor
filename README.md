# Sistema de Monitoreo del Plan de Descontaminación

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1%2B-green)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Sistema de Monitoreo para Plan de Descontaminación

Sistema de gestión y monitoreo para el Plan de Descontaminación de Concón, Quinteros y Puchuncaví, permitiendo el seguimiento del avance de medidas por los diferentes organismos participantes y ofreciendo transparencia a la ciudadanía.

## 🚀 Características

- ✅ Multi-usuario y multi-rol: Superadmin, Admin SMA, Organismos y Ciudadanos
- 📊 Dashboards interactivos con visualización del avance global y por componente
- 📝 Gestión de medidas organizadas por componentes temáticos
- 📋 Registro de avances por cada organismo responsable
- 📈 Generación de reportes en múltiples formatos (web, PDF)
- 🔔 Sistema de notificaciones en tiempo real con envío por correo electrónico
- 🔑 Sistema de permisos basado en roles
- 🔍 Auditoría de todas las acciones realizadas en el sistema
- 🌐 API REST completa con documentación Swagger/OpenAPI
- 🖥️ Portal público para transparencia ciudadana

## 📋 Requisitos

- Python 3.10+
- PostgreSQL 13+
- Pip y Virtualenv

## 🛠️ Instalación

1. Clonar el repositorio

```bash
git clone https://github.com/your-username/sma_monitor.git
cd sma_monitor
```

2. Crear y activar entorno virtual

```bash
python -m venv .venv

# En Windows
.venv\Scripts\activate

# En macOS/Linux
source .venv/bin/activate
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
```

4. Configurar la base de datos PostgreSQL

```bash
# Crear la base de datos
createdb plan_descontaminacion

# Configurar credenciales en .env (si archivo .env no existe, crearlo en la raíz del directorio)
cp .env.example .env
# Editar .env con tus credenciales
```

El archivo .env debe contener:

```
DB_NAME=plan_descontaminacion
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicación
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=SMA Monitor <tu_correo@gmail.com>
```

5. Aplicar migraciones

```bash
python manage.py migrate
```

6. Crear superusuario

```bash
python manage.py createsuperuser
```

7. Iniciar el servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en:

- http://127.0.0.1:8000/ -> Para acceder al portal público
- http://127.0.0.1:8000/api/v1/ -> Acceder a la interfaz de API
- http://127.0.0.1:8000/admin/ -> Para acceder al Admin de Django
- http://127.0.0.1:8000/api/v1/swagger/ -> Para acceder a la API mediante Swagger

## 🏗️ Estructura del Proyecto

```
sma_monitor/
├── apps/
│   ├── api/                # API REST
│   ├── auditorias/         # Sistema de auditoría
│   ├── medidas/            # Gestión de medidas y avances
│   ├── notificaciones/     # Sistema de notificaciones
│   ├── organismos/         # Gestión de organismos
│   ├── publico/            # Portal público
│   ├── reportes/           # Generación de reportes
│   └── usuarios/           # Autenticación y perfiles
├── ppda_core/              # Configuración principal
├── templates/              # Plantillas HTML
├── static/                 # Archivos estáticos
├── media/                  # Archivos subidos por usuarios
├── requirements.txt        # Dependencias
└── manage.py               # Script de gestión de Django
```

## 🧩 Modelos Principales

### Organismos

- **TipoOrganismo**: Categorías de organismos participantes
- **Organismo**: Entidades responsables de implementar medidas
- **ContactoOrganismo**: Personas de contacto de cada organismo

### Medidas

- **Componente**: Áreas temáticas del plan de descontaminación
- **Medida**: Acciones específicas del plan
- **AsignacionMedida**: Relación entre medidas y organismos responsables
- **RegistroAvance**: Seguimiento del avance de cada medida

### Usuarios

- **Usuario**: Extensión del modelo User de Django con roles específicos
- **Perfil**: Información adicional del usuario
- **HistorialAcceso**: Registro de accesos al sistema

### Notificaciones

- **TipoNotificacion**: Categorías de notificaciones del sistema
- **Notificacion**: Mensajes enviados a los usuarios
- **ConfiguracionNotificaciones**: Preferencias de notificación por usuario

### Reportes

- **TipoReporte**: Definición de reportes disponibles
- **ReporteGenerado**: Instancias de reportes generados
- **ParametroReporte**: Configuración personalizable para reportes

## 📊 Dashboard

El sistema ofrece múltiples dashboards especializados:

### Dashboard SMA

- Estadísticas globales del plan
- Avance por componente
- Organismos con mejor y peor desempeño
- Medidas próximas a vencer
- Medidas retrasadas
- Últimos avances registrados

### Dashboard Organismo

- Medidas asignadas al organismo
- Estadísticas de cumplimiento
- Próximos vencimientos
- Historiales de avance

## 🔔 Sistema de Notificaciones

El sistema cuenta con un completo módulo de notificaciones:

- Notificaciones en tiempo real en la interfaz
- Envío de notificaciones por correo electrónico
- Alertas automáticas para medidas próximas a vencer
- Notificaciones de nuevas asignaciones
- Registro de avances
- Panel de gestión de notificaciones

## 📊 API REST

La API del sistema permite la integración con otras aplicaciones y el consumo de datos desde el frontend.

### Documentación

- Swagger UI: /api/swagger/
- ReDoc: /api/redoc/
- Esquema OpenAPI: /api/schema/

### Endpoints principales

- /api/v1/organismos/: Gestión de organismos
- /api/v1/medidas/: Administración de medidas
- /api/v1/registros-avance/: Registro de avances
- /api/v1/componentes/: Componentes del plan
- /api/v1/dashboard/: Datos resumidos para visualización
- /api/v1/notificaciones/: Gestión de notificaciones

## 👥 Perfiles de Usuario

### Superadmin

- Acceso completo al sistema
- Configuración técnica
- Gestión de usuarios y permisos

### Admin SMA

- Gestión de medidas y componentes
- Seguimiento de avances
- Validación de datos
- Generación de reportes

### Organismos

- Registro de avances en medidas asignadas
- Visualización de sus medidas y plazos
- Recepción de notificaciones
- Consulta de reportes específicos

### Ciudadanos

- Visualización del avance general del plan
- Consulta de información pública
- Acceso a reportes públicos

## 🧪 Testing

Para ejecutar las pruebas:

```bash
# Ejecutar todas las pruebas
python manage.py test

# Ejecutar pruebas específicas
python manage.py test apps.medidas
```

## 🧪 Tests

El proyecto incluye pruebas automatizadas para asegurar la correcta funcionalidad de los modelos, serializadores y asignaciones.

### 🧬 Cobertura de Tests

Se han implementado tests para:

- **Modelos (`Medida`)**:
  - Creación válida
  - Restricciones de unicidad (`codigo`)
  - Validaciones de `estado` y `prioridad` (`choices`)
  - Ordenamiento por `codigo`
- **Serializadores (`MedidaSerializer`)**:
  - Creación de medida vía serializer
  - Actualización de medida vía serializer
- **Modelo de Asignación (`AsignacionMedida`)**:
  - Creación de una asignación válida
  - Representación en string (str)

### 📁 Ubicación de los tests

Todos los tests están organizados dentro del directorio raíz `tests/`:

```
tests/
├── test_modelo_medidas.py
├── test_medida_serializer.py
└── test_asignacion_medida.py
```

### ▶️ Cómo ejecutarlos

#### Ejecutar todos los tests:

```bash
pytest --ds=ppda_core.settings
```

#### Ejecutar un archivo específico:

```bash
pytest tests/test_modelo_medidas.py --ds=ppda_core.settings
```

#### Ejecutar una clase de test específica:

```bash
pytest tests/test_modelo_medidas.py::TestMedidasModel --ds=ppda_core.settings
```

#### Ejecutar un método específico:

```bash
pytest tests/test_modelo_medidas.py::TestMedidasModel::test_medida_creation --ds=ppda_core.settings
```

## 🚀 Despliegue

El sistema está preparado para despliegue en la nube:

### Plataformas soportadas

- Render.com
- Heroku
- AWS
- Google Cloud
- Azure

### Bases de datos soportadas

- PostgreSQL local
- PostgreSQL en Neon.tech
- AWS RDS
- Google Cloud SQL

### Preparación para producción

```bash
# Recolectar archivos estáticos
python manage.py collectstatic

# Verificar configuración
python manage.py check --deploy
```

### Despliegue en Render y Neon

Se incluyen archivos de configuración para despliegue automático en Render conectado a una base de datos PostgreSQL en Neon:

- build.sh: Script de construcción para Render
- render.yaml: Configuración del servicio web
- Soporte para variables de entorno seguras

## 📝 Contribución

1. Haz un fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Empuja a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## 📧 Contacto

Para soporte o consultas: grupo5@chinorios.com

Desarrollado por Grupo 5 © 2025
