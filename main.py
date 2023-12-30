from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import bluetooth

app = Flask(__name__, template_folder='C:\\Users\\User\\Desktop\\ProiectSI\\templetates')
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app)

server_address = '98:DA:50:01:A3:FD'
port = 1
sock = None

dynamic_value = 0

def establish_bluetooth_connection():
    global sock
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((server_address, port))

def send_mail(mailTo, value, subject):
    CLIENT_SECRET_FILE = 'credentials.json'
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    emailMsg = value
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = mailTo
    mimeMessage['subject'] = subject
    mimeMessage.attach(MIMEText(emailMsg, 'plain', 'utf-8'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()


@app.route('/')
def index():
    return render_template('index.html', dynamic_value=dynamic_value)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update_dynamic_value', {'dynamic_value': dynamic_value})

email_to = None  # Variabila globala pentru adresa de e-mail

@socketio.on('update_email')
def handle_update_email(data):
    global email_to
    email_to = data['email']

@socketio.on('request_dynamic_value')
def handle_request_dynamic_value():
    global dynamic_value
    new_dynamic_value = 0
    dynamic_value = new_dynamic_value
    if sock is None:
        establish_bluetooth_connection()

    data_received = sock.recv(1024).decode().strip()
    values = data_received.split('\n')
    if data_received:
        dynamic_value = float(values[0])
        print(f"Received dynamic value from Bluetooth: {dynamic_value}")
    if new_dynamic_value > 32 and email_to:
        print(new_dynamic_value)
        send_mail(email_to, f': Atentie,este prea cald in casa')

    elif new_dynamic_value < 19 and email_to:
        send_mail(email_to, f': Atentie,este prea frig in casa')


    emit('update_dynamic_value', {'dynamic_value': dynamic_value}, broadcast=True)


@socketio.on('send_current_temperature')
def handle_send_current_temperature():
    if email_to:
        send_mail(email_to, f'Temperatura actuala: {dynamic_value}')


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5002)
