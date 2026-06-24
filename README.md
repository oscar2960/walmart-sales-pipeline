<<<<<<< HEAD
# 🛒 Walmart Sales Analytics — Pipeline CI/CD Completo

Proyecto académico que implementa un **pipeline de Integración Continua y
Entrega Continua (CI/CD)** de extremo a extremo para una aplicación de
análisis de ventas, usando **Python, PostgreSQL, Docker, Docker Compose,
Jenkins, Travis CI, Codeship, Git/GitHub y Ngrok**.

Sirve como portafolio profesional para demostrar competencias de
**Arquitectura DevOps**, **Ingeniería de Datos** y **Desarrollo de
Software**.

---

## 📑 Tabla de contenido

1. [Descripción del caso de negocio](#-descripción-del-caso-de-negocio)
2. [Arquitectura del proyecto](#-arquitectura-del-proyecto)
3. [Estructura de directorios](#-estructura-de-directorios)
4. [Requisitos previos](#-requisitos-previos)
5. [Opción A — Ejecución rápida con Docker Compose](#-opción-a--ejecución-rápida-con-docker-compose-recomendado)
6. [Opción B — Ejecución local sin Docker](#-opción-b--ejecución-local-sin-docker)
7. [Ejecutar las pruebas unitarias](#-ejecutar-las-pruebas-unitarias)
8. [Variables de entorno](#-variables-de-entorno)
9. [Usar el dataset real de Kaggle](#-usar-el-dataset-real-de-kaggle)
10. [Configurar Jenkins + Ngrok + Webhook de GitHub](#-configurar-jenkins--ngrok--webhook-de-github)
11. [Configurar Travis CI](#-configurar-travis-ci)
12. [Configurar Codeship](#-configurar-codeship)
13. [Flujo de Git recomendado](#-flujo-de-git-recomendado)
14. [Solución de problemas (Troubleshooting)](#-solución-de-problemas-troubleshooting)
15. [Checklist de aprendizaje](#-checklist-de-aprendizaje-cubierto)
16. [Licencia](#-licencia)

---

## 📊 Descripción del caso de negocio

La aplicación simula un proceso real de **Ingeniería de Datos**:

1. **Extract**: lee un archivo `Walmart_Sales.csv` con columnas
   `Store, Date, Weekly_Sales, Holiday_Flag, Temperature, Fuel_Price, CPI,
   Unemployment` (formato del dataset público *Walmart Sales* de Kaggle).
2. **Transform**: limpia tipos de datos, parsea fechas, elimina duplicados
   y descarta filas inválidas.
3. **Load**: inserta los registros limpios en una tabla `sales` de
   **PostgreSQL** (inserción idempotente, evita duplicar datos en cargas
   repetidas).
4. **Analyze**: calcula métricas de negocio:
   - Ventas totales.
   - Ranking de ventas por tienda.
   - Promedio semanal de ventas por tienda.
   - Mejor y peor tienda.
   - Comparativo semana feriado vs. semana regular.
   - Tendencia mensual de ventas.
5. **Report**: imprime un reporte formateado por consola.

Todo el flujo (1 a 5) se ejecuta automáticamente al iniciar el contenedor
de la aplicación.

---

## 🏗 Arquitectura del proyecto

```
┌─────────────┐     git push      ┌──────────────┐
│  Desarrollador │ ───────────────▶ │   GitHub     │
└─────────────┘                    └──────┬───────┘
                                           │ Webhook
                  ┌────────────────────────┼─────────────────────────┐
                  │                        │                         │
                  ▼                        ▼                         ▼
           ┌─────────────┐         ┌──────────────┐          ┌─────────────┐
           │  Travis CI  │         │   Codeship   │          │   Ngrok     │
           │ (build/test)│         │ (build/test) │          │ (tunneling) │
           └─────────────┘         └──────────────┘          └──────┬──────┘
                                                                     │
                                                                     ▼
                                                              ┌─────────────┐
                                                              │   Jenkins   │
                                                              │ (Pipeline)  │
                                                              └──────┬──────┘
                                                                     │ docker build / compose up
                                                                     ▼
                                                       ┌───────────────────────┐
                                                       │   Docker Compose      │
                                                       │ ┌─────────┐ ┌────────┐│
                                                       │ │PostgreSQL│ │  App   ││
                                                       │ └─────────┘ └────────┘│
                                                       └───────────────────────┘
```

Cada plataforma de CI cubre un propósito distinto para fines didácticos:

| Herramienta  | Rol en el pipeline                                            |
|--------------|-----------------------------------------------------------------|
| **Travis CI**  | Integración Continua basada en la nube, disparada por `push`/PR a GitHub. |
| **Codeship**   | Integración Continua alternativa basada en contenedores (`codeship-services.yml` / `codeship-steps.yml`). |
| **Jenkins**    | Automatización local/self-hosted, disparada por **Webhook de GitHub** vía **Ngrok**. Construye la imagen, prueba y despliega con Docker Compose. |

---

## 📂 Estructura de directorios

```
walmart-sales-pipeline/
├── app/                        # Código de la aplicación
│   ├── __init__.py
│   ├── config.py               # Configuración centralizada (env vars)
│   ├── db.py                   # Capa de acceso a PostgreSQL
│   ├── etl.py                  # Extract-Transform-Load
│   ├── metrics.py               # Cálculo de métricas de negocio
│   └── main.py                 # Punto de entrada / orquestador
├── tests/                      # Pruebas unitarias e integración
│   ├── __init__.py
│   ├── test_etl.py
│   ├── test_metrics.py
│   └── test_db.py              # Se omite si no hay PostgreSQL disponible
├── sql/
│   └── schema.sql              # DDL de la tabla "sales"
├── data/
│   └── Walmart_Sales.csv       # Dataset de muestra (sintético, reemplazable)
├── Jenkinsfile                 # Pipeline declarativo de Jenkins
├── Dockerfile                  # Imagen de la aplicación
├── docker-compose.yml          # Orquestación App + PostgreSQL
├── .travis.yml                 # Pipeline de Travis CI
├── codeship-services.yml       # Servicios de Codeship
├── codeship-steps.yml          # Pasos del pipeline de Codeship
├── requirements.txt            # Dependencias de producción
├── requirements-dev.txt        # Dependencias de desarrollo/test
├── .env.example                # Plantilla de variables de entorno
├── .gitignore
├── .dockerignore
├── setup.cfg                   # Configuración de flake8
├── pytest.ini                  # Configuración de pytest
├── Makefile                    # Comandos abreviados (make up, make test, ...)
├── LICENSE
└── README.md                   # Este archivo
```

---

## ✅ Requisitos previos

Instala lo siguiente en tu máquina (Windows con WSL2, Linux o macOS):

| Herramienta       | Versión sugerida | Verificar instalación        |
|-------------------|-------------------|-------------------------------|
| Python            | 3.11+             | `python3 --version`           |
| Docker            | 24+               | `docker --version`            |
| Docker Compose    | v2 (plugin)       | `docker compose version`      |
| Git               | cualquiera reciente | `git --version`              |
| Cuenta de GitHub  | —                 | —                              |
| Jenkins           | 2.4xx LTS         | (se instala en el paso 10)     |
| Ngrok             | v3                | `ngrok version`                |
| Cuenta Travis CI  | travis-ci.com     | —                              |
| Cuenta Codeship   | codeship.com      | —                              |

> 💡 Si usas `docker-compose` (con guion, v1) en lugar de `docker compose`
> (plugin v2), simplemente sustituye el comando en los ejemplos de abajo.

---

## 🚀 Opción A — Ejecución rápida con Docker Compose (recomendado)

Esta es la forma más simple y profesional de ejecutar todo el proyecto.

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/walmart-sales-pipeline.git
cd walmart-sales-pipeline
```

### Paso 2 — (Opcional) Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env si deseas cambiar usuario/contraseña/puerto de PostgreSQL
```

### Paso 3 — Levantar PostgreSQL + la aplicación

```bash
docker compose up --build
```

Lo que ocurre internamente:

1. Se construye la imagen Docker de la aplicación (`Dockerfile`).
2. Se levanta el contenedor `walmart_postgres` (PostgreSQL 15) y se espera
   a que su *healthcheck* (`pg_isready`) confirme que está listo.
3. Se levanta el contenedor `walmart_app`, que:
   - Espera la conexión a PostgreSQL (reintentos automáticos).
   - Crea el esquema (`sql/schema.sql`) si no existe.
   - Carga el CSV de `data/Walmart_Sales.csv` si la tabla está vacía.
   - Calcula las métricas y las imprime por consola.

### Paso 4 — Revisar la salida

Deberías ver en consola un reporte similar a:

```
====================================================================
                  REPORTE DE VENTAS - WALMART
====================================================================
Total de registros analizados : 30
Ventas totales                : $ 47,081,882.34
Tienda con mejores ventas      : #2  ($ 21,670,334.67)
Tienda con peores ventas       : #3  ($ 9,144,644.34)
...
```

### Paso 5 — Detener los servicios

```bash
docker compose down -v
```

> 🛠 También puedes usar los atajos del `Makefile`: `make up`, `make down`,
> `make logs`, `make test`, `make clean`.

---

## 💻 Opción B — Ejecución local sin Docker

Útil para desarrollo y debugging directo del código Python.

### Paso 1 — Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

### Paso 2 — Levantar solo PostgreSQL con Docker

```bash
docker compose up -d postgres
```

### Paso 3 — Configurar variables de entorno

```bash
cp .env.example .env
# DB_HOST debe ser "localhost" para ejecución fuera de Docker
export $(grep -v '^#' .env | xargs)   # Linux/macOS
```

### Paso 4 — Ejecutar la aplicación

```bash
python -m app.main
```

---

## 🧪 Ejecutar las pruebas unitarias

El proyecto separa dos tipos de pruebas:

- **Unitarias puras** (`test_etl.py`, `test_metrics.py`): no requieren base
  de datos, corren en cualquier entorno (local o CI).
- **Integración** (`test_db.py`): requieren PostgreSQL real; se **omiten
  automáticamente** (`skip`) si no detectan una base de datos disponible.

### Con PostgreSQL levantado (recomendado, prueba todo)

```bash
docker compose up -d postgres
source venv/bin/activate
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Sin PostgreSQL (solo unitarias puras)

```bash
pytest tests/test_etl.py tests/test_metrics.py -v
```

### Análisis estático (lint)

```bash
flake8 app tests --max-line-length=120
```

---

## 🔐 Variables de entorno

| Variable       | Descripción                              | Valor por defecto          |
|----------------|--------------------------------------------|------------------------------|
| `DB_HOST`      | Host de PostgreSQL                        | `localhost`                  |
| `DB_PORT`      | Puerto de PostgreSQL                      | `5432`                       |
| `DB_USER`      | Usuario de la base de datos               | `walmart_user`                |
| `DB_PASSWORD`  | Contraseña de la base de datos            | `walmart_pass`                |
| `DB_NAME`      | Nombre de la base de datos                | `walmart_sales`                |
| `CSV_PATH`     | Ruta al archivo CSV de ventas             | `data/Walmart_Sales.csv`       |

---

## 📁 Usar el dataset real de Kaggle

El archivo `data/Walmart_Sales.csv` incluido es una **muestra sintética**
(30 filas, 3 tiendas) generada únicamente para que el proyecto funcione
"out of the box". Para un análisis real:

1. Descarga el dataset público **"Walmart Sales"** desde Kaggle (búscalo
   como *Walmart Store Sales Forecasting* o *Walmart Sales Dataset*).
2. Verifica que conserve las columnas:
   `Store, Date, Weekly_Sales, Holiday_Flag, Temperature, Fuel_Price, CPI,
   Unemployment` (formato de fecha `DD-MM-YYYY`).
3. Sobrescribe el archivo `data/Walmart_Sales.csv`.
4. Si ya habías ejecutado el proyecto antes, limpia la base para forzar
   una nueva carga:

   ```bash
   docker compose down -v   # elimina el volumen de PostgreSQL
   docker compose up --build
   ```

---

## 🔧 Configurar Jenkins + Ngrok + Webhook de GitHub

Esta sección demuestra **automatización de despliegues** disparada
automáticamente por cambios en GitHub.

### Paso 1 — Levantar Jenkins (vía Docker, recomendado)

```bash
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(which docker):/usr/bin/docker \
  jenkins/jenkins:lts
```

Obtén la contraseña inicial:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Abre `http://localhost:8080`, pega la contraseña y completa el asistente
de instalación.

### Paso 2 — Instalar plugins necesarios

En **Manage Jenkins → Plugins**, instala:

- `Git plugin`
- `GitHub Integration Plugin`
- `Pipeline`
- `Docker Pipeline`
- `Credentials Binding`

### Paso 3 — Crear el Pipeline Job

1. **New Item → Pipeline** → nómbralo `walmart-sales-pipeline`.
2. En **Pipeline → Definition**, selecciona
   **Pipeline script from SCM**.
3. **SCM**: Git → URL del repositorio → rama `main`.
4. **Script Path**: `Jenkinsfile`.
5. Guarda.

### Paso 4 — Instalar y ejecutar Ngrok

Ngrok expone tu Jenkins local (`localhost:8080`) a Internet, para que
GitHub pueda enviarle el Webhook.

```bash
# Instalación (ver https://ngrok.com/download según tu sistema operativo)
ngrok config add-authtoken <TU_TOKEN_DE_NGROK>
ngrok http 8080
```

Ngrok mostrará algo como:

```
Forwarding   https://abcd-1234.ngrok-free.app -> http://localhost:8080
```

Copia esa URL HTTPS.

### Paso 5 — Configurar el Webhook en GitHub

1. Ve al repositorio en GitHub → **Settings → Webhooks → Add webhook**.
2. **Payload URL**: `https://abcd-1234.ngrok-free.app/github-webhook/`
   (¡no olvides la barra final!).
3. **Content type**: `application/json`.
4. **Which events?**: selecciona *Just the push event* (o *Pull requests*
   si también quieres disparar en PRs).
5. Guarda.

### Paso 6 — Probar el disparo automático

```bash
git commit --allow-empty -m "test: disparar pipeline de Jenkins"
git push origin main
```

En Jenkins deberías ver un nuevo build iniciado automáticamente en el job
`walmart-sales-pipeline`.

> ⚠️ Ngrok en su plan gratuito genera una URL nueva cada vez que se
> reinicia. Si la URL cambia, deberás actualizar el Webhook en GitHub.

---

## ☁️ Configurar Travis CI

1. Inicia sesión en [travis-ci.com](https://travis-ci.com) con tu cuenta
   de GitHub.
2. Ve a tu perfil → **Settings** → activa el repositorio
   `walmart-sales-pipeline`.
3. El archivo `.travis.yml` ya está en la raíz del repositorio, por lo que
   Travis lo detectará automáticamente en el próximo `git push`.
4. (Opcional) Si necesitas variables sensibles, configúralas en
   **Repository Settings → Environment Variables** en lugar de
   hardcodearlas en `.travis.yml`.
5. Realiza un `git push` y observa el build en el dashboard de Travis:
   - Instalación de dependencias.
   - Lint (`flake8`).
   - Pruebas unitarias e integración contra PostgreSQL real (vía addon).
   - Build de la imagen Docker.

---

## 🚢 Configurar Codeship

1. Inicia sesión en [codeship.com](https://app.codeship.com) y conecta tu
   cuenta de GitHub.
2. Crea un nuevo proyecto **Basic** (basado en contenedores) y selecciona
   el repositorio `walmart-sales-pipeline`.
3. Codeship detectará automáticamente `codeship-services.yml` y
   `codeship-steps.yml` en la raíz del proyecto.
4. Configura las variables de entorno necesarias en
   **Project Settings → Environment Variables** si decides no
   hardcodearlas (en este proyecto académico se incluyen directamente en
   los YAML por simplicidad).
5. Cada `push` disparará automáticamente:
   - `lint` → análisis estático con flake8.
   - `unit_and_integration_tests` → pytest contra PostgreSQL real.
   - `smoke_test_app` → ejecución funcional completa de la app.

---

## 🌿 Flujo de Git recomendado

```bash
git checkout -b feature/nueva-metrica
# ... realizar cambios ...
git add .
git commit -m "feat: agregar métrica de crecimiento mensual"
git push origin feature/nueva-metrica
# Abrir Pull Request en GitHub -> Travis CI / Codeship corren automáticamente
# Tras aprobar y mergear a main -> Webhook dispara Jenkins -> build y despliegue
```

Convención de commits sugerida (estilo *Conventional Commits*):
`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`.

---

## 🩺 Solución de problemas (Troubleshooting)

| Síntoma                                                   | Causa probable / Solución                                                  |
|------------------------------------------------------------|------------------------------------------------------------------------------|
| `connection refused` al conectar a PostgreSQL              | El contenedor `postgres` aún no terminó de iniciar. `app` reintenta automáticamente (`wait_for_db`); si persiste, revisa `docker compose logs postgres`. |
| `relation "sales" does not exist`                           | El esquema no se creó. Verifica que `sql/schema.sql` esté montado y ejecuta `docker compose down -v && docker compose up --build` para reiniciar el volumen. |
| Los tests de `test_db.py` se omiten (`SKIPPED`)              | Comportamiento esperado si no hay PostgreSQL accesible en `DB_HOST:DB_PORT`. Levanta `docker compose up -d postgres` antes de correr pytest. |
| El Webhook de GitHub no dispara Jenkins                     | Verifica que la URL de Ngrok termine en `/github-webhook/`, que Ngrok siga corriendo, y revisa **Recent Deliveries** en GitHub → Webhooks para ver el código de respuesta. |
| `docker build` falla por permisos                           | Asegúrate de que tu usuario pertenezca al grupo `docker` (Linux) o que Docker Desktop esté corriendo (Windows/macOS). |
| Travis CI no detecta el repositorio                         | Confirma que el repo esté activado en **travis-ci.com** (no en la versión legacy `.org`) y que tengas permisos de administrador sobre él. |
| Codeship no encuentra los archivos YAML                     | Deben llamarse exactamente `codeship-services.yml` y `codeship-steps.yml` y estar en la raíz del repositorio. |

---

## 🎓 Checklist de aprendizaje cubierto

- [x] Control de versiones con **Git** (branching, commits semánticos).
- [x] Gestión de repositorios en **GitHub** (Webhooks, Pull Requests).
- [x] Integración Continua con **Travis CI** (`.travis.yml`).
- [x] Integración Continua con **Codeship** (`codeship-services.yml`,
  `codeship-steps.yml`).
- [x] Automatización de despliegues con **Jenkins** (`Jenkinsfile`
  declarativo, disparado por Webhook).
- [x] Uso de **Docker** y **Docker Compose** (multi-servicio, healthchecks,
  volúmenes, variables de entorno).
- [x] Uso de **PostgreSQL** como base de datos relacional (esquema
  idempotente, índices, restricciones únicas).
- [x] **Webhooks GitHub → Jenkins** para disparo automático de pipelines.
- [x] Exposición local de servicios mediante **Ngrok**.
- [x] Pruebas unitarias y de integración con **pytest**.
- [x] Buenas prácticas de **Ingeniería de Datos** (ETL, validación,
  deduplicación, tipado).

---

## 📄 Licencia

Este proyecto se distribuye bajo licencia **MIT** con fines exclusivamente
académicos y de portafolio profesional. Ver el archivo [`LICENSE`](LICENSE).
=======


>>>>>>> ec6fe39da851920b3c9d6f0b502f95493843febd
