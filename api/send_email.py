import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Importamos make_response para controlar mejor los headers de la respuesta
from flask import Flask, request, jsonify, make_response 

# Inicializar Flask (necesario para manejar la solicitud HTTP)
app = Flask(__name__)

# --- CONFIGURACIÓN DE SMTP: LECTURA OBLIGATORIA DESDE VARIABLES DE ENTORNO ---
# CRÍTICO: Leer todos los valores de os.environ.get para evitar conflictos de constantes
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com") # Usar fallback por si acaso
SMTP_PORT_RAW = os.environ.get("SMTP_PORT", "587")

try:
    SMTP_PORT = int(SMTP_PORT_RAW)
except ValueError:
    # Si la variable de puerto no es un número, forzamos el valor por defecto
    SMTP_PORT = 587

SMTP_TIMEOUT = 15 # Aumentamos el timeout a 15 segundos

@app.route('/api/send_email', methods=['POST'])
def handler():
    """
    Ruta principal (handler) de la Función Serverless de Vercel.
    Procesa el POST del formulario, verifica la configuración y envía el correo.
    """
    
    # 1. Obtener y verificar variables de entorno CRUCIALES (Configuradas en Vercel Dashboard)
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    SENDER_PASSWORD_RAW = os.environ.get("SENDER_PASSWORD")
    RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

    if not all([SENDER_EMAIL, SENDER_PASSWORD_RAW, RECIPIENT_EMAIL]):
        # Mensaje de error si faltan credenciales
        print("ERROR: Faltan variables de entorno cruciales (SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL).")
        response = make_response(jsonify({
            "status": "error", 
            "message": "Error de configuración interna. Faltan credenciales de correo en Vercel."
        }), 500)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # CORRECCIÓN CRUCIAL: Eliminar cualquier espacio en blanco en la contraseña
    # Esto soluciona problemas con las Contraseñas de Aplicación de 16 caracteres de Google.
    SENDER_PASSWORD = SENDER_PASSWORD_RAW.replace(" ", "")

    # 2. Extracción y Validación de datos del formulario
    form_data = request.form
    
    # Campos obligatorios desde el HTML
    name = form_data.get('name')
    reply_to = form_data.get('_replyto') 
    project_type = form_data.get('Tipo de Proyecto')
    
    # Campos opcionales
    project_details = form_data.get('Detalles del Proyecto', 'No se proporcionaron detalles')
    budget = form_data.get('Presupuesto Estimado', 'No especificado')

    # Validación de datos del formulario (si faltan campos obligatorios)
    if not all([name, reply_to, project_type]):
        response = make_response(jsonify({
            "status": "error",
            "message": "Faltan datos obligatorios (Nombre, Email o Tipo de Proyecto)."
        }), 400)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # 3. Construcción del Cuerpo del Mensaje
    subject = f"Nuevo Contacto - {project_type} - De: {name}"
    
    body = f"""
    ¡Nueva Solicitud de Contacto desde el Formulario Web!
    -----------------------------------------------------
    Nombre Completo: {name}
    Correo Electrónico: {reply_to}
    
    Tipo de Proyecto/Servicio: {project_type}
    Presupuesto Estimado: {budget}

    Detalles del Mensaje:
    {project_details}
    -----------------------------------------------------
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg['Reply-To'] = reply_to 
    msg.attach(MIMEText(body, 'plain'))

    # 4. Envío del Correo
    try:
        # LÓGICA CONDICIONAL DE CONEXIÓN
        if SMTP_PORT == 465:
            # Usar SMTP_SSL para el puerto 465 (SSL/TLS implícito)
            server_class = smtplib.SMTP_SSL
            print("INFO: Usando conexión SMTPS (puerto 465).")
        else:
            # Usar SMTP para cualquier otro puerto (ej. 587, STARTTLS explícito)
            server_class = smtplib.SMTP
            print(f"INFO: Usando conexión SMTP (puerto {SMTP_PORT}).")
            
        # Conexión al servidor SMTP
        with server_class(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
            
            # Si el puerto no es 465, intentamos starttls
            if SMTP_PORT != 465:
                server.starttls()
            
            # Autenticación: Usamos la clave sin espacios
            server.login(SENDER_EMAIL, SENDER_PASSWORD) 
            
            # Envío
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
            print(f"Correo enviado exitosamente a {RECIPIENT_EMAIL}")

        # Éxito: Devolver JSON 200 OK
        response = make_response(jsonify({
            "status": "success", 
            "message": "¡Solicitud enviada con éxito!"
        }), 200)

    except smtplib.SMTPAuthenticationError as e:
        # Error específico de credenciales (clave incorrecta o bloqueada)
        print(f"Error de autenticación SMTP: {e}")
        response = make_response(jsonify({
            "status": "error",
            "message": "Error 500: Fallo en credenciales. Verifica SENDER_PASSWORD o si el email tiene 2FA activado."
        }), 500)
        
    except Exception as e:
        # Error general de conexión (timeout, servidor inaccesible, bloqueo de red)
        print(f"Fallo general al enviar el correo: {e}")
        # Comprobar si es un error de conexión
        if "timeout" in str(e).lower() or "connection refused" in str(e).lower() or "getaddrinfo failed" in str(e).lower():
            error_message = "Error de red: El servidor de correo no respondió (Timeout/Conexión bloqueada). Intenta cambiar el puerto."
        else:
            error_message = "Error interno inesperado. Revisa logs de Vercel."
            
        response = make_response(jsonify({
            "status": "error",
            "message": error_message
        }), 500)

    # 5. Añadir el encabezado CORS (Access-Control-Allow-Origin) a la respuesta final
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
