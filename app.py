# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade

from flask import Flask

from flask import render_template
from flask import request
from flask import jsonify, make_response

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


# Código usado en las prácticas
def notificarActualizacionTemperaturaHumedad():
    pusher_client = pusher.Pusher(
        app_id='1766037',
        key='fc838f52101ac3c0e022',
        secret='f9f1bc16656c8d474a72',
        cluster='us2',
        ssl=True
    )

    pusher_client.trigger("canalRegistrosTemperaturaHumedad", "registroTemperaturaHumedad", args)

@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("""
    SELECT Id_Experiencias, Nombre_Apellido, Comentario, Calificacion FROM tst0_experiencias
    ORDER BY Id_Experiencias DESC
    LIMIT 10 OFFSET 0
    """)
    registros = cursor.fetchall()

    con.close()

    return make_response(jsonify(registros))

@app.route("/guardar", methods=["POST"])
def guardar():
    if not con.is_connected():
        con.reconnect()

    id          = request.form["id"]
    Nombre_Apellido = request.form["Nombre_Apellido"]
    Comentario = request.form["Comentario"]
    Calificacion   = request.form["Calificacion"]
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE tst0_experiencia SET
        Nombre_Apellido = %s,
        Comentario     = %s,
        Calificacion     = %s
        WHERE Id_Experiencias = %s
        """
        val = (id, Nombre_Apellido, Comentario, Calificacion)
    else:
        sql = """
        INSERT INTO  tst0_experiencia (Nombre_Apellido, Comentario, Calificacion)
                        VALUES (%s,          %s,      %s)
        """
        val =                  (Nombre_Apellido, Comentario, Calificacion)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionTemperaturaHumedad()

    return make_response(jsonify({}))

@app.route("/editar", methods=["GET"])
def editar():
    if not con.is_connected():
        con.reconnect()

    id = request.args["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Experiencias, Nombre_Apellido, Comentario, Calificacion FROM tst0_experiencia
    WHERE Id_Experiencias = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/eliminar", methods=["POST"])
def eliminar():
    if not con.is_connected():
        con.reconnect()

    id = request.form["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM tst0_experiencia
    WHERE Id_Experiencias = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionTemperaturaHumedad()

    return make_response(jsonify({}))
