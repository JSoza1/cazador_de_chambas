# 🤖 Cazador De Chambas

Este proyecto es un sistema automatizado diseñado para buscar y postular a empleos en diversas plataformas como **Bumeran** y **Computrabajo**, entre **otros sitios** especializados y bolsas de trabajo corporativas. Está construido en Python utilizando **Selenium** para la automatización del navegador.

El objetivo de este código no es solo funcional, sino **educativo**. Está documentado extensamente para explicar cómo funciona cada parte.

---

## 🚀 Características

*   **Multi-Sitio & Extensible**: Compatible nativamente con Bumeran, Computrabajo, Andreani, EducaciónIT, BBVA, Vicente López, UTN Talentia y EmpleosIT. Gracias a su arquitectura modular, agregar nuevas bolsas de trabajo es una tarea sencilla.
*   **Notificaciones en Tiempo Real**: Envía alertas a **Telegram** cada vez que encuentra una oferta interesante.
*   **Control Interactivo**: Si respondes a una notificación en Telegram con **"ya lo vi"**, **"listo"**, **"este no"**, **"ya esta"** o **"paso"**, el bot dejará de mostrarte esa oferta por 15 días.
*   **Modular y Escalable**: Estructura preparada para agregar más sitios (LinkedIn, etc.) sin reescribir el núcleo.
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
job-search/
├── main.py                # 🧠 CEREBRO: El punto de entrada. Coordina qué bots activar.
├── .env                   # 🔒 SECRETOS: Credenciales de sitios y de Telegram (privado).
├── .gitignore             # 🙈 SEGURIDAD: Define qué archivos ocultar a Git.
├── seen_jobs.json         # 💾 MEMORIA: Base de datos local de ofertas ya vistas (auto-generado).
├── last_update.json       # 📡 TELEGRAM: Control de mensajes leídos (auto-generado).
├── requirements.txt       # 📦 DEPENDENCIA: Lista de librerías necesarias.
└── src/                   # ⚙️ CÓDIGO FUENTE
    ├── config.py          # ⚙️ CONFIGURACIÓN: Carga variables y keywords.
    ├── history.py         # 🧠 MEMORIA: Lógica de persistencia de ofertas.
    ├── listener.py        # 👂 ESCUCHA: Procesa respuestas del usuario en Telegram.
    ├── notifications.py   # 📢 ALERTAS: Sistema de envío de mensajes a Telegram.
    ├── driver.py          # 🚗 MOTOR: Maneja el navegador (Chrome) y modos Headless.
    └── sites/             # 🌐 SITIOS: Aquí vive la lógica de cada página web.
        ├── base.py        # 📋 PLANTILLA: Define reglas comunes (login, buscar, notificar).
        ├── andreani.py    # 👷 BOT 3: Implementación para Andreani.
        ├── bbva.py        # 👷 BOT 5: Implementación para BBVA.
        ├── educacionit.py # 👷 BOT 4: Implementación para EducaciónIT.
        ├── empleosit.py   # 👷 BOT 8: Implementación para EmpleosIT.
        ├── talentia.py    # 👷 BOT 7: Implementación para UTN Talentia.
        ├── vicentelopez.py# 👷 BOT 6: Implementación para Vicente López.
        ├── bumeran.py     # 👷 BOT 1: Implementación para Bumeran.
        └── computrabajo.py# 👷 BOT 2: Implementación para Computrabajo.
```

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

## 🛠️ Instalación en PC (Windows/Linux)

### 1. Prerrequisitos
Se requiere tener instalado **Python** y **Google Chrome**.

### 2. Pasos
1.  Clonar el repositorio.
2.  Instalar dependencias: `pip install -r requirements.txt`
3.  Crear `.env` basándose en `.env.example`.

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

# Instalar librerías Python
pip install -r requirements.txt

# Configurar Secretos (Manual)
cp .env.example .env
nano .env
# (Aquí debes borrar los ejemplos y escribir tus claves reales. Ctrl+O para guardar, Ctrl+X para salir)
```

### 3. Ejecutar
```bash
python main.py
```
El bot detectará automáticamente que está en Android y usará la configuración especial.

### 🔋 Tips para que NO se duerma Termux (Importante)
Android mata los procesos en segundo plano para ahorrar batería. Para evitar que el bot se apague a las pocas horas:

1.  **Activar Wakelock:** Baja la barra de notificaciones de Android, busca la de Termux, expándela y pulsa **"Acquire wakelock"**.
2.  **Quitar Restricciones:** Ve a *Ajustes > Batería > Optimización de batería*, busca **Termux** y selecciona **"No optimizar"** o "Sin restricciones".

---

Hecho por **Jsoza**
