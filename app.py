from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Ruta API simple que devuelve JSON
@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hola mundo desde el backend Flask 🚀"})

# Ruta que renderiza el HTML desde /templates/index.html
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask en http://0.0.0.0:8080", flush=True)
    app.run(host='0.0.0.0', port=8080)