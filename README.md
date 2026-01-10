# 🤖 Cazador De Chambas

Este proyecto es un sistema automatizado diseñado para buscar y postular a empleos en diversas plataformas (**Bumeran** y **Computrabajo**). Está construido en Python utilizando **Selenium** para la automatización del navegador.

El objetivo de este código no es solo funcional, sino **educativo**. Está documentado extensamente para explicar cómo funciona cada parte.

---

## 🚀 Características

*   **Multi-Sitio**: Compatible con Bumeran y Computrabajo.
*   **Notificaciones en Tiempo Real**: Envía alertas a **Telegram** cada vez que encuentra una oferta interesante.
*   **Modular y Escalable**: Estructura preparada para agregar más sitios (LinkedIn, etc.) sin reescribir el núcleo.
*   **Filtrado Inteligente**: Ignora ofertas no aplicables y duplicadas.
*   **Seguro**: Uso de variables de entorno para la protección de credenciales.
*   **Portable**: Diseñado pensando en su futura migración a servidores o dispositivos Android (vía Termux).

---

## ⚙️ Tecnologías Utilizadas

*   **Python 3.10+**: Lenguaje principal.
*   **Selenium WebDriver**: Automatización del navegador (Chrome).
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
├── requirements.txt       # 📦 DEPENDENCIA: Lista de librerías necesarias.
└── src/                   # ⚙️ CÓDIGO FUENTE
    ├── config.py          # ⚙️ CONFIGURACIÓN: Carga variables y keywords.
    ├── notifications.py   # 📢 ALERTAS: Sistema de envío de mensajes a Telegram.
    ├── driver.py          # 🚗 MOTOR: Maneja el navegador (Chrome) y modos Headless.
    └── sites/             # 🌐 SITIOS: Aquí vive la lógica de cada página web.
        ├── base.py        # 📋 PLANTILLA: Define reglas comunes (login, buscar, notificar).
        ├── bumeran.py     # 👷 BOT 1: Implementación para Bumeran.
        └── computrabajo.py# 👷 BOT 2: Implementación para Computrabajo.
```

---

## 🛠️ Instalación y Configuración

### 1. Prerrequisitos
Se requiere tener instalado **Python** y **Google Chrome**.

### 2. Instalar Dependencias
Abrir una terminal en la carpeta del proyecto y ejecutar:
```bash
pip install -r requirements.txt
```
(Incluye `selenium`, `requests` y `python-dotenv`).

### 3. Configurar Credenciales (.env)
1.  Crear un archivo llamado `.env` en la raíz del proyecto.
2.  Configurar las variables de entorno de .env.example.

---

Hecho por **Jsoza**
