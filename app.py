import os
import boto3
import logging
from flask import Flask, request, render_template, redirect, url_for, flash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

print("🔍 Starting app.py initialization")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

print(f"✅ SECRET_KEY loaded: {app.secret_key}")

S3_BUCKET = os.environ.get("S3_BUCKET")
AWS_REGION = os.environ.get("AWS_REGION")

print(f"✅ AWS_REGION: {AWS_REGION}")
print(f"✅ S3_BUCKET: {S3_BUCKET}")

try:
    s3 = boto3.client('s3', region_name=AWS_REGION)
    print("✅ S3 client initialized")
except Exception as e:
    print(f"🔥 ERROR creating S3 client: {e}")
    raise

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

        if file:
            s3.upload_fileobj(file, S3_BUCKET, file.filename)
            flash('File successfully uploaded to S3')
            return redirect(url_for('upload_file'))

    return render_template('upload.html')

if __name__ == "__main__":
    print("🚀 Starting Flask server on 0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080)