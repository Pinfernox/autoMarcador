# AutoMarcador Studio ⚽

Generador automático de resúmenes de partidos con marcadores deportivos superpuestos.

## 📋 Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado:

1.  **Python 3.9+**
2.  **FFmpeg**: Es el motor que procesa el video.

### 🛠️ Cómo instalar FFmpeg

* **Windows:** Descarga el ejecutable desde [ffmpeg.org](https://ffmpeg.org/download.html), extrae el archivo y añade la carpeta `bin` a tus Variables de Entorno (PATH).
* **Mac:** `brew install ffmpeg`
* **Linux:** `sudo apt install ffmpeg`

## 🚀 Instalación del Proyecto

1.  Clona el repositorio:
    ```bash
    git clone [https://github.com/tu-usuario/automarcador.git](https://github.com/tu-usuario/automarcador.git)
    ```
2.  Instala las dependencias de Python:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ejecuta el servidor:
    ```bash
    uvicorn main:app --reload
    ```

## ⚖️ Licencia y Créditos

Este proyecto utiliza **FFmpeg** bajo la licencia LGPLv2.1. FFmpeg es una marca registrada de Fabrice Bellard. Este proyecto no está asociado oficialmente con el proyecto FFmpeg.

## ⚙️ Configuración de FFmpeg (Obligatorio)

Este proyecto requiere FFmpeg para procesar los videos. El programa no se incluye en este repositorio y debe instalarse manualmente.

### 🟡 Windows

1.  **Descargar:** Ve a [ffmpeg.org](https://www.gyan.dev/ffmpeg/builds/) y descarga la versión *git-full* o *release-essentials* (archivo .7z o .zip).
2.  **Descomprimir:** Extrae la carpeta y renómbrala a `ffmpeg`. Muévela a una ubicación segura, por ejemplo: `C:\ffmpeg`.
3.  **Configurar Variables de Entorno (PATH):**
    * En el buscador de Windows escribe: *"Editar las variables de entorno del sistema"*.
    * Haz clic en el botón **"Variables de entorno..."**.
    * En el apartado "Variables del sistema" (abajo), busca la variable llamada **Path** y haz doble clic o "Editar".
    * Haz clic en "Nuevo" y pega la ruta de la carpeta `bin` que está dentro de lo que descargaste.
        * Ejemplo: `C:\ffmpeg\bin`
    * Acepta todas las ventanas.
4.  **Verificar:** Abre una nueva terminal (CMD o PowerShell) y escribe `ffmpeg -version`. Si salen letras y números, ¡ya está listo!

### 🟢 Mac / Linux

* **Mac:** Ejecuta `brew install ffmpeg` en la terminal.
* **Linux:** Ejecuta `sudo apt install ffmpeg` en la terminal.

## 🐳 Ejecución con Docker (Opción Rápida)

Si no quieres instalar FFmpeg manualmente en tu sistema, puedes usar Docker.

1.  **Construir la imagen:**
    ```bash
    docker build -t automarcador .
    ```

2.  **Ejecutar el contenedor:**
    ```bash
    docker run -p 8000:8000 automarcador
    ```

3.  Abre tu navegador en `http://localhost:8000`
