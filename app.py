import os
import boto3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

# Configurar conexión a base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

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

# Página principal (después de login)
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
            ExtraArgs={
                "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        )

        return render_template('home.html', success="✅ Archivo subido correctamente a S3.")

    except Exception as e:
        print(f"🔥 Error al subir a S3: {e}")
        return render_template('home.html', error="🔥 Error al subir el archivo a S3.")

# Dashboard: últimos 20 servicios agendados
@app.route('/dashboard')
def dashboard():
    session = Session()
    try:
        query = text("""
        SELECT
            c.id_cliente,
            c.propietario,
            c.celular,
            s.servicio,
            f.precio,
            d.fecha_agendamiento
        FROM fact_cita f
        JOIN dim_cliente c ON f.id_cliente = c.id_cliente
        JOIN dim_servicio s ON f.id_servicio = s.id_servicio
        JOIN dim_fecha d ON f.id_fecha = d.id_fecha
        ORDER BY d.fecha_agendamiento DESC
        LIMIT 12
        """)
        result = session.execute(query).fetchall()
        return render_template('dashboard.html', citas=result)
    except Exception as e:
        print(f"🔥 Error al consultar la base de datos: {e}")
        return render_template('dashboard.html', citas=[], error="Error al cargar datos.")
    finally:
        session.close()

# Ejecutar app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)