# 🤖 Cazador De Chambas

Este proyecto es un sistema automatizado diseñado para buscar y postular a empleos en diversas plataformas como **Bumeran** y **Computrabajo**, entre **otros sitios** especializados y bolsas de trabajo corporativas. Está construido en Python utilizando **Selenium** para la automatización del navegador.

El objetivo de este código no es solo funcional, sino **educativo**. Está documentado extensamente para explicar cómo funciona cada parte.

---

## 🚀 Características

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
├── profile/               # 👤 COOKIES: Carpeta del perfil de Chrome para guardar sesiones.
└── src/                   # ⚙️ CÓDIGO FUENTE
    ├── config.py          # ⚙️ CONFIGURACIÓN: Carga variables y keywords.
    ├── history.py         # 🧠 MEMORIA: Lógica de persistencia de ofertas.
    ├── listener.py        # 👂 ESCUCHA: Procesa respuestas del usuario en Telegram.
    ├── keywords_manager.py # 🧠 MEMORIA: Gestión de palabras clave y filtros de idioma (JSON).
    ├── notifications.py   # 📢 ALERTAS: Sistema de envío de mensajes a Telegram.
    ├── driver.py          # 🚗 MOTOR: Maneja el navegador (Chrome) y modos Headless.
    └── sites/             # 🌐 SITIOS: Aquí vive la lógica de cada página web.
        ├── base.py        # 📋 PLANTILLA: Define reglas comunes (filtrado, notificar, filtro de idioma).

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

## ☁️ Instalación en la Nube (GitHub Actions) - RECOMENDADO

La forma más eficiente y desatendida de correr este bot es configurarlo para que se ejecute automáticamente cada 4 horas usando los servidores gratuitos de Github, sin gastar la batería de tu celular o PC.

1.  **Sube este código a tu propio repositorio** (puede ser Público o Privado).
2.  **Configura los secretos:** En GitHub, ve a la pestaña **Settings > Secrets and variables > Actions**. Crea un "New repository secret" llamado `TELEGRAM_BOT_TOKEN` con tu token, y otro llamado `TELEGRAM_CHAT_ID` con tu ID.
3.  **Habilita permisos de escritura (¡CRÍTICO!):** Para que el bot pueda guardar su memoria (`seen_jobs.json`) tras cada búsqueda, debe poder hacer "commits" en tu código. Ve a **Settings > Actions > General**, haz *scroll* hasta abajo a la sección **Workflow permissions**, selecciona **Read and write permissions** y dale a **Save**.
4.  ¡Listo! GitHub detectará automáticamente el archivo `.github/workflows/cazador.yml` y comenzará a correr el script según el cronograma estipulado.
    *   Podrás ver cómo arranca cada 4 horas desde la pestaña **Actions**.
    *   El bot es amnésico en la nube, pero hemos diseñado una arquitectura de "Self-Commit". Gracias a los permisos de escritura del paso 3, el bot sobreescribirá y subirá los archivos `seen_jobs.json`, lo que garantiza que pueda recordar los empleos observados entre una sesión y otra.

---

## 🛠️ Ejecución Local (PC / Servidor Propio)

Si prefieres ejecutar el bot en tu propia máquina o usar Termux en Android para pruebas:

### 1. Preparación
1.  **Clonar el código**: `git clone https://github.com/Jsoza1/cazador_de_chambas.git` y entra a la carpeta.
2.  **Configurar variables**: Copia el archivo `.env.example`, renómbralo a `.env` y rellena tus datos de Telegram.

### 2. Ejecutar
El código incluye scripts "inteligentes" que crean automáticamente los entornos virtuales e instalan las dependencias.
*   **En Windows**: Haz doble clic en `run_bot.bat`.
*   **En Linux o Android (Termux)**:  
    ```bash
    chmod +x run.sh
    ./run.sh
    ```
*(En Termux, recuerda activar el wakelock de Android y quitar las restricciones de batería si planeas dejarlo todo el día).*

---

Realizado por **JSoza**
