import os
import boto3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Página de inicio de sesión
@app.route('/')
def index():
    return render_template('index.html')

# Procesar login
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'admin' and password == 'admin':
        return redirect(url_for('home'))
    else:
        error = 'Usuario o contraseña incorrectos.'
        return render_template('index.html', error=error)

# Página principal protegida
@app.route('/home')
def home():
    return render_template('home.html')

# Subir archivo a S3
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')

    if not file or file.filename == '':
        return render_template('home.html', error="No seleccionaste ningún archivo.")

    filename = secure_filename(file.filename)

    if not filename.endswith('.xlsx'):
        return render_template('home.html', error="Solo se permiten archivos .xlsx")

    try:
        s3 = boto3.client(
            's3',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

        s3.upload_fileobj(
            Fileobj=file,
            Bucket=os.getenv("AWS_BUCKET_NAME"),
            Key=f"{filename}",
            ExtraArgs={"ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
        )

        return render_template('home.html', success="✅ Archivo subido correctamente a S3.")

    except Exception as e:
        print(f"🔥 Error al subir a S3: {e}")
        return render_template('home.html', error="🔥 Error al subir el archivo a S3.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)