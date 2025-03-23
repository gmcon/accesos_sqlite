from flask import Flask, request, render_template_string
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DB_PATH = "registros.db"

# Crear la base de datos si no existe
def inicializar_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alumno_id TEXT NOT NULL,
                fecha TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

inicializar_db()

@app.route("/registro", methods=["POST"])
def registrar():
    datos = request.get_json(force=True)
    alumno_id = datos.get("id")
    fecha = datos.get("fecha", datetime.utcnow().isoformat())

    if not alumno_id:
        return {"estado": "error", "mensaje": "Falta ID"}, 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO registros (alumno_id, fecha) VALUES (?, ?)", (alumno_id, fecha))
    conn.commit()
    conn.close()

    print(f"✔ Registro guardado: {alumno_id} - {fecha}")
    return {"estado": "ok"}, 200

@app.route("/ver")
def ver():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT alumno_id, fecha FROM registros ORDER BY fecha DESC")
    filas = cursor.fetchall()
    conn.close()

    tabla_html = """
    <html><head><title>Registros</title></head><body>
    <h2>Registros de Acceso</h2>
    <table border="1" cellpadding="6" cellspacing="0">
    <tr><th>Alumno</th><th>Fecha</th></tr>
    {}
    </table></body></html>
    """.format(''.join(f"<tr><td>{alumno}</td><td>{fecha}</td></tr>" for alumno, fecha in filas))
    return tabla_html

@app.route("/")
def home():
    return "✅ Backend con SQLite operativo"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
