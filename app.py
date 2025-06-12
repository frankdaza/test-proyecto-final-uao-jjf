import os
import boto3
import logging
from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv

# ✅ Cargar variables del .env antes que nada (solo en local)
if os.environ.get("FLASK_ENV") != "production":
    load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

print("🔍 Starting app.py initialization")

app = Flask(__name__)

# ✅ Cargar variables de entorno
app.secret_key = os.environ.get('SECRET_KEY')

AWS_REGION = os.environ.get("AWS_REGION")
S3_BUCKET = os.environ.get("S3_BUCKET")

print(f"✅ SECRET_KEY loaded: {app.secret_key}")
print(f"✅ AWS_REGION: {AWS_REGION}")
print(f"✅ S3_BUCKET: {S3_BUCKET}")

# Inicializar cliente de S3 usando boto3
try:
    # Si quieres usar un profile localmente
    if os.environ.get("FLASK_ENV") != "production" and os.environ.get("AWS_PROFILE"):
        session = boto3.Session(profile_name=os.environ.get("AWS_PROFILE"))
        s3 = session.client('s3', region_name=AWS_REGION)
    else:
        s3 = boto3.client('s3', region_name=AWS_REGION)

    print("✅ S3 client initialized")
except Exception as e:
    print(f"🔥 ERROR creating S3 client: {e}")
    raise

# Extensiones permitidas (solo Excel)
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                # Subir archivo a S3
                s3.upload_fileobj(
                    file,
                    S3_BUCKET,
                    file.filename,
                    ExtraArgs={'ContentType': file.content_type}
                )

                flash('✅ File successfully uploaded to S3!')
                return redirect(url_for('upload_file'))

            except Exception as e:
                logger.error(f"🔥 Error uploading file to S3: {e}")
                flash('❌ Error uploading file. Please try again.')
                return redirect(request.url)
        else:
            flash('❌ Invalid file type. Please upload an Excel file (.xls or .xlsx).')
            return redirect(request.url)

    return render_template('upload.html')

if __name__ == "__main__":
    print("🚀 Starting Flask server on 0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080)