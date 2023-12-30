from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import bluetooth
from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__, template_folder='C:\\Users\\User\\Desktop\\ProiectSI\\templetates')
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app)

server_address = '98:DA:50:01:A3:FD'
port = 1
sock = None

dynamic_value = 0
last_email_sent = None
in_interval = True

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


data = {
    'Temperatura': [18, 22, 25, 30, 35, 19, 21, 33],
    'Avertizare': [0, 0, 0, 1, 1, 0, 0, 1]
}

df = pd.DataFrame(data, columns=['Temperatura', 'Avertizare'])

X_train = df[['Temperatura']]
y_train = df['Avertizare']

# Antrenare model RandomForest
model = RandomForestClassifier()
model.fit(X_train, y_train)

@app.route('/')
def index():
    return render_template('index.html', dynamic_value=dynamic_value)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update_dynamic_value', {'dynamic_value': dynamic_value})

email_to = None

@socketio.on('update_email')
def handle_update_email(data):
    global email_to
    email_to = data['email']

@socketio.on('request_dynamic_value')
def handle_request_dynamic_value():
    global dynamic_value, last_email_sent, in_interval, email_sent
    new_dynamic_value = 0
    dynamic_value = new_dynamic_value
    if sock is None:
        establish_bluetooth_connection()

    data_received = sock.recv(1024).decode().strip()
    values = data_received.split('\n')
    if data_received:
        dynamic_value = float(values[0])
        print(f"Received dynamic value from Bluetooth: {dynamic_value}")

        # Atribuire implicită pentru in_interval și email_sent
        in_interval = in_interval if 'in_interval' in locals() else True
        email_sent = email_sent if 'email_sent' in locals() else False

        if not in_interval:
            # Verificăm dacă temperatura a revenit în interval
            if 19 <= dynamic_value <= 32:
                in_interval = True
                email_sent = False

        if in_interval and not email_sent:
            if dynamic_value > 32 and email_to:
                print(dynamic_value)
                send_mail(email_to, 'Depasire temperatura', f'Atentie este prea cald in casa')
                last_email_sent = 'cool'
                email_sent = True
            elif dynamic_value < 19 and email_to:
                send_mail(email_to, 'Depasire temperatur', f'Atentie este prea cald in casa')
                last_email_sent = 'warm'
                email_sent = True

    emit('update_dynamic_value', {'dynamic_value': dynamic_value}, broadcast=True)


@socketio.on('send_current_temperature')
def handle_send_current_temperature():
    if email_to:
        send_mail(email_to, f'Temperatura actuala este de: {dynamic_value} grade Celsius', ': Actualizare temperatura')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5002)
