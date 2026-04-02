# 🤖 Cazador De Chambas

Este proyecto es un sistema automatizado diseñado para buscar y postular a empleos en diversas plataformas como **Bumeran** y **Computrabajo**, entre **otros sitios** especializados y bolsas de trabajo corporativas. Está construido en Python utilizando **Selenium** para la automatización del navegador.

El objetivo de este código no es solo funcional, sino **educativo**. Está documentado extensamente para explicar cómo funciona cada parte.

---

## 🚀 Características

*   **Soporte LinkedIn Avanzado**: Incluye un bot robusto para LinkedIn con manejo de perfiles persistentes (cookies) y scroll inteligente para evadir bloqueos.
*   **Multi-Sitio & Extensible**: Compatible nativamente con Bumeran, Computrabajo, Andreani, EducaciónIT, BBVA, Vicente López, UTN Talentia y EmpleosIT. Gracias a su arquitectura modular, agregar nuevas bolsas de trabajo es una tarea sencilla.
*   **Notificaciones en Tiempo Real**: Envía alertas a **Telegram** cada vez que encuentra una oferta interesante.
*   **Control Interactivo**: Si respondes a una notificación en Telegram con **"ya lo vi"**, **"listo"**, **"este no"**, **"ya esta"** o **"paso"**, el bot dejará de mostrarte esa oferta por 15 días.
*   **Filtro de Idioma**: Detecta automáticamente si la descripción de un puesto está en inglés, portugués o italiano y lo descarta sin notificarte. Configurable desde Telegram.
*   **Modular y Escalable**: Estructura preparada para agregar más sitios (Zonajobs, etc.) sin reescribir el núcleo.
*   **Filtrado Inteligente (Regex)**: Ignora ofertas no aplicables y duplicadas, distinguiendo palabras completas (ej: diferencia 'Sr' de 'Ssr').
*   **Seguro**: Uso de variables de entorno para la protección de credenciales.
*   **Portable**: Diseñado pensando en su futura migración a servidores o dispositivos Android (vía Termux).

---

## ⚙️ Tecnologías Utilizadas

*   **Python 3.10+**: Lenguaje principal.
*   **Selenium WebDriver**: Automatización del navegador.
*   **Termux (Android) / Linux**: Entorno de ejecución móvil.
*   **Requests**: Comunicación HTTP para envío de mensajes a Telegram.
*   **Python-Dotenv**: Gestión segura de variables de entorno.
*   **Git**: Control de versiones.

---

## 📂 Estructura del Proyecto

Entender la estructura es clave para modificar el código:

```text
cazador_de_chambas/
├── main.py                # 🧠 CEREBRO: El punto de entrada. Coordina qué bots activar.
├── .env                   # 🔒 SECRETOS: Credenciales de sitios y de Telegram (privado).
├── .gitignore             # 🙈 SEGURIDAD: Define qué archivos ocultar a Git.
├── seen_jobs.json         # 💾 MEMORIA: Base de datos local de ofertas ya vistas (auto-generado).
├── keywords.json          # 💾 MEMORIA: Palabras clave y filtros de idioma (auto-generado).
├── last_update.json       # 📡 TELEGRAM: Control de mensajes leídos (auto-generado).
├── requirements.txt       # 📦 DEPENDENCIA: Lista de librerías necesarias.
├── profile/               # 👤 COOKIES: Carpeta del perfil de Chrome (guarda sesión de LinkedIn).
└── src/                   # ⚙️ CÓDIGO FUENTE
    ├── config.py          # ⚙️ CONFIGURACIÓN: Carga variables y keywords.
    ├── history.py         # 🧠 MEMORIA: Lógica de persistencia de ofertas.
    ├── listener.py        # 👂 ESCUCHA: Procesa respuestas del usuario en Telegram.
    ├── keywords_manager.py # 🧠 MEMORIA: Gestión de palabras clave y filtros de idioma (JSON).
    ├── notifications.py   # 📢 ALERTAS: Sistema de envío de mensajes a Telegram.
    ├── driver.py          # 🚗 MOTOR: Maneja el navegador (Chrome) y modos Headless.
    └── sites/             # 🌐 SITIOS: Aquí vive la lógica de cada página web.
        ├── base.py        # 📋 PLANTILLA: Define reglas comunes (filtrado, notificar, filtro de idioma).
        ├── linkedin.py    # 🆕 LINKEDIN: Bot especializado con scroll y cookies persistentes.
        ├── andreani.py    # 👷 BOT: Implementación para Andreani.
        ├── bbva.py        # 👷 BOT: Implementación para BBVA.
        ├── bumeran.py     # 👷 BOT: Implementación para Bumeran.
        ├── computrabajo.py# 👷 BOT: Implementación para Computrabajo.
        ├── educacionit.py # 👷 BOT: Implementación para EducaciónIT.
        ├── empleosit.py   # 👷 BOT: Implementación para EmpleosIT.
        ├── talentia.py    # 👷 BOT: Implementación para UTN Talentia.
        └── vicentelopez.py# 👷 BOT: Implementación para Vicente López.
```

---

## 🎮 Comandos de Telegram

Una vez configurado el bot, puedes controlarlo dinámicamente desde el chat sin reiniciar:

### 🚫 Palabras Negativas de Título
Se aplican al **título** del puesto. Si el título contiene alguna, se ignora.

| Acción | Comando Principal | Alias | Ejemplo |
|:---|:---|:---|:---|
| Agregar negativa | `/addneg <palabra>` | `/menos`, `/an` | `/menos wordpress` |
| Eliminar negativa | `/delneg <palabra>` | `/sacarmenos`, `/dn` | `/dn php` |
| Ver negativas | `/listneg` | `/vermenos`, `/ln` | `/ln` |

### ✅ Palabras Positivas de Título
El título debe contener al menos una de estas para ser notificado.

| Acción | Comando Principal | Alias | Ejemplo |
|:---|:---|:---|:---|
| Agregar positiva | `/addpos <palabra>` | `/mas`, `/ap` | `/mas typescript` |
| Eliminar positiva | `/delpos <palabra>` | `/sacarmas`, `/dp` | `/dp react` |
| Ver positivas | `/listpos` | `/vermas`, `/lp` | `/lp` |

### 🌐 Filtro de Idioma (descripción del puesto)
Se aplica a la **descripción** del puesto, solo cuando el título ya pasó los filtros anteriores. Si la descripción contiene alguna de estas frases, el puesto se descarta silenciosamente (no se notifica por Telegram, pero sí aparece en el log de consola). Acepta frases con espacios, sin comillas.

| Acción | Comando Principal | Alias | Ejemplo |
|:---|:---|:---|:---|
| Agregar frase | `/addidioma <frase>` | `/ai` | `/addidioma requirements` |
| Eliminar frase | `/sacaridioma <frase>` | `/si` | `/sacaridioma requirements` |
| Ver frases | `/veridioma` | `/vi` | `/vi` |

> Por defecto ya incluye frases comunes de descripciones en **inglés**, **portugués** e **italiano**.

### 🗃️ Otras Acciones

| Acción | Comando | Notas |
|:---|:---|:---|
| Archivar oferta | `ya lo vi` / `listo` / `paso` | Responder al mensaje del bot con la oferta |
| Ayuda / Comandos | `/comandos` | También `/help`, `/ayuda` |
| Apagar Bot | `/stop` | También `/shutdown`, `/apagar`, `/exit` |

---

## 🔍 Cómo funciona el filtrado

El bot aplica los filtros en este orden para cada oferta encontrada:

```
1. ¿Ya fue vista antes?           → Si sí, ignorar.
2. ¿Contiene palabra negativa?    → Si sí, ignorar el título.
3. ¿Contiene palabra positiva?    → Si no, ignorar el título.
4. ¿Descripción en otro idioma?   → Si sí, ignorar silenciosamente (log en consola).
5. ✅ ¡Match! → Notificar por Telegram.
```

El filtro de idioma funciona abriendo el detalle de cada oferta que ya pasó los pasos 1-3, leyendo el texto completo y buscando frases características de descripciones en inglés, portugués o italiano.

---

## 📲 Configuración de Notificaciones (Telegram)

Para que el bot te avise al celular, necesitas dos datos sencillos:

1.  **Crear el Bot:**
    *   Abre Telegram y busca a **@BotFather**.
    *   Envía el comando `/newbot`.
    *   Sigue las instrucciones (ponle nombre y usuario).
    *   Te dará un **TOKEN** (ej: `123456:ABC-DEF...`). Guárdalo.

2.  **Obtener tu ID:**
    *   Busca a **@userinfobot** en Telegram.
    *   Dale a "Iniciar" o envía cualquier mensaje.
    *   Te responderá con tu ID numérico (ej: `987654321`).

3.  **Configurar:**
    *   Pon estos datos en tu archivo `.env` en los campos `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`.
    *   ⚠️ **Importante:** Debes enviar un mensaje "Hola" a tu nuevo bot para inicializar la conversación antes de ejecutar el script.

---

## 🛠️ Instalación y Configuración

Se recomienda encarecidamente usar un entorno virtual para evitar conflictos de dependencias con otros proyectos.

### 1. Prerrequisitos
*   **Python 3.10+** instalado.
*   **Google Chrome** (en PC) o **Chromium** (en Termux).

### 2. Configuración en PC (Windows/Linux)
1.  **Clonar el repositorio**: `git clone https://github.com/Jsoza1/cazador_de_chambas.git`
2.  **Crear Entorno Virtual**:
    *   Windows: `python -m venv venv`
    *   Linux: `python3 -m venv venv`
3.  **Instalar Dependencias**:
    *   Windows: `.\venv\Scripts\pip install -r requirements.txt`
    *   Linux: `./venv/bin/pip install -r requirements.txt`
4.  **Configurar Secretos**: Copiar `.env.example` a `.env` y completar los datos de Telegram.

### 3. Cómo Ejecutar
*   **Windows**: Simplemente haz doble clic en `run_bot.bat`. Este archivo activa el entorno y lanza el bot automáticamente.
*   **Linux / Android (Termux)**:
    ```bash
    # Ejecutar con el script de conveniencia
    bash run.sh

    # O bien manualmente (activar y correr)
    source venv/bin/activate
    python main.py
    ```

---

## 📱 Instalación en Android (Termux)

Guía paso a paso para convertir un celular en un servidor de búsqueda.

### 1. Preparación de Termux
Descargar Termux desde **F-Droid** (no Play Store). Ejecutar los siguientes comandos:

```bash
# Actualizar sistema
pkg update -y && pkg upgrade -y

# Instalar herramientas básicas
pkg install python git nano -y

# Habilitar repositorio de terceros (Necesario para Chromium headless)
pkg install tur-repo -y

# Instalar dependencias gráficas (Evita errores de gtk3)
pkg install x11-repo -y

# Instalar Chromium
pkg install chromium-browser -y
```

### 2. Configuración del Proyecto
```bash
# Clonar repositorio
git clone https://github.com/Jsoza1/cazador_de_chambas.git
cd cazador_de_chambas

# Crear entorno virtual e instalar librerías
python -m venv venv
./venv/bin/pip install -r requirements.txt

# Configurar Secretos (Manual)
cp .env.example .env
nano .env
# (Aquí debes borrar los ejemplos y escribir tus claves reales. Ctrl+O para guardar, Ctrl+X para salir)
```

### 3. Ejecutar
```bash
./venv/bin/python main.py
```
El bot detectará automáticamente que está en Android y usará la configuración especial.

### 🔋 Tips para que NO se duerma Termux (Importante)
Android mata los procesos en segundo plano para ahorrar batería. Para evitar que el bot se apague a las pocas horas:

1.  **Activar Wakelock:** Baja la barra de notificaciones de Android, busca la de Termux, expándela y pulsa **"Acquire wakelock"**.
2.  **Quitar Restricciones:** Ve a *Ajustes > Batería > Optimización de batería*, busca **Termux** y selecciona **"No optimizar"** o "Sin restricciones".

---

Hecho por **Jsoza**
