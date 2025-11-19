import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Importamos make_response para controlar mejor los headers de la respuesta
from flask import Flask, request, jsonify, make_response 

# Inicializar Flask (necesario para manejar la solicitud HTTP)
app = Flask(__name__)

# --- Constantes de Configuración de SMTP (Fijas para Gmail) ---
# Usamos Gmail por defecto y el puerto estándar para TLS
SMTP_SERVER = "smtp.gmail.com"
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
    SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
    RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        print("ERROR: Faltan variables de entorno cruciales (SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL).")
        response = make_response(jsonify({
            "status": "error", 
            "message": "Error de configuración interna. Faltan credenciales de correo en Vercel."
        }), 500)
        # Añadir encabezado CORS a la respuesta de error
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # 2. Extracción y Validación de datos del formulario
    form_data = request.form
    
    # Campos obligatorios desde el HTML
    name = form_data.get('name')
    reply_to = form_data.get('_replyto') # El email del cliente (CRUCIAL para Reply-To)
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
    # CRUCIAL: Usar Reply-To para que al responder al correo, respondas al cliente
    msg['Reply-To'] = reply_to 
    msg.attach(MIMEText(body, 'plain'))

    # 4. Envío del Correo
    try:
        # Conexión al servidor SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
            server.starttls()  # Protocolo seguro
            
            # Autenticación: ESTE es el punto que falla si SENDER_PASSWORD no es la App Password
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
            "message": "Error 500: Fallo en credenciales. Usa la Contraseña de Aplicación de Google."
        }), 500)
        
    except Exception as e:
        # Error general de conexión (timeout, servidor inaccesible)
        print(f"Fallo general al enviar el correo: {e}")
        response = make_response(jsonify({
            "status": "error",
            "message": "Error al conectar o enviar el correo. Revisa logs de Vercel."
        }), 500)

    # 5. Añadir el encabezado CORS (Access-Control-Allow-Origin) a la respuesta final
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
