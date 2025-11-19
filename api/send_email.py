# Este archivo DEBE estar en un subdirectorio llamado 'api/' para que Vercel lo detecte.
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Vercel usa la función 'handler' para Serverless Functions en Python
# Importamos Flask para manejar la estructura de la petición web POST
from flask import Flask, request, jsonify

# --- Configuration ---
# IMPORTANTE: En Vercel, estas variables de entorno se configuran en el Dashboard.

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))

# La dirección de correo que recibirá las solicitudes del formulario
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "your_receiving_email@example.com") 

# Inicializar Flask (necesario para manejar la solicitud HTTP)
app = Flask(__name__)

def send_form_email(form_data):
    """
    Conecta a un servidor SMTP y envía un correo electrónico con el contenido del formulario.
    """
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("ERROR: Credenciales de correo no configuradas en Vercel.")
        return False

    # 1. Extracción de datos del formulario (usando los nombres del formulario en form.html)
    name = form_data.get('name', 'N/A')
    email = form_data.get('_replyto', 'N/A') # Campo del email del remitente
    project_type = form_data.get('Tipo de Proyecto', 'N/A')
    project_details = form_data.get('Detalles del Proyecto', 'No se proporcionaron detalles')
    budget = form_data.get('Presupuesto Estimado', 'No especificado')

    # 2. Construir el cuerpo del correo
    body = f"""
    ¡Nueva Solicitud de Contacto desde el Formulario Web!
    -----------------------------------------------------
    Nombre Completo: {name}
    Correo Electrónico: {email}
    
    Tipo de Proyecto/Servicio: {project_type}
    Presupuesto Estimado: {budget}

    Detalles del Mensaje:
    {project_details}
    -----------------------------------------------------
    """
    
    # 3. Crear el objeto de mensaje de correo
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f"Nueva Solicitud de Contacto - {name} ({project_type})"
    msg.attach(MIMEText(body, 'plain'))

    try:
        # 4. Conexión y envío
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
            print(f"Correo enviado exitosamente a {RECIPIENT_EMAIL}")
            return True
    except Exception as e:
        print(f"Fallo al enviar el correo: {e}")
        return False

# La función handler de Vercel (la que se ejecuta al recibir la petición)
@app.route('/api/send_email', methods=['POST'])
def handler():
    """
    Ruta de Flask/Vercel Serverless Function para recibir la solicitud POST.
    """
    # Request.form extrae datos del formulario multipart/form-data
    form_data = request.form
    
    if not form_data:
        return jsonify({"message": "No se recibieron datos del formulario."}), 400
        
    success = send_form_email(form_data)
    
    if success:
        # Respuesta de éxito
        return jsonify({"message": "¡Solicitud enviada con éxito!"}), 200
    else:
        # Respuesta de error
        return jsonify({"message": "El servidor falló al enviar el correo. Revise logs y variables de entorno."}), 500

# Esta línea es para compatibilidad con Vercel
if __name__ == '__main__':
    # Esto solo se ejecuta si se inicia localmente. Vercel llama a la función `handler` directamente.
    app.run(debug=True, port=3000)
