from flask import Flask

from flask import render_template
from flask import request

import pusher

import mysql.connector
import datetime
import pytz

con = mysql.connector.connect(
  host="185.232.14.52",
  database="u760464709_tst_sep",
  user="u760464709_tst_sep_usr",
  password="dJ0CIAFF="
)

app = Flask(__name__)

@app.route("/")
def index():
    con.close()
    return render_template("app.html")

@app.route("/alumnos")
def alumnos():
    con.close()
    return render_template("alumnos.html")

@app.route("/alumnos/guardar", methods=["POST"])
def alumnosGuardar():
    con.close()
    matricula      = request.form["txtMatriculaFA"]
    nombreapellido = request.form["txtNombreApellidoFA"]
    return f"Matrícula {matricula} Nombre y Apellido {nombreapellido}"

@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM sensor_log")

    registros = cursor.fetchall()

    return registros

@app.route("/registrar", methods=["GET"])
def registrar():
    pusher_client = pusher.Pusher(
        app_id="1714541",
        key="2df86616075904231311",
        secret="2f91d936fd43d8e85a1a",
        cluster="us2",
        ssl=True
    )

    pusher_client.trigger("canalRegistrosTemperaturaHumedad", "registroTemperaturaHumedad", request.args)
